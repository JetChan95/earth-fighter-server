from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_openapi3 import OpenAPI, Info, Tag
from pydantic import BaseModel
from db_dao import EarthFighterDAO
from logger import LoggerFactory
from config_manager import ConfigManager
from ultils import generate_invite_code
from schemas import *

dao = EarthFighterDAO()
logger = LoggerFactory.getLogger()
cfg = ConfigManager()

app_name =  "earth_fighter"

# 配置信息
info = Info(title="Earth fighter Api", version="1.0.0")

# 配置安全方案
jwt = {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT"
}
security_schemes = {"jwt": jwt}
security = [{"jwt": []}]

app = OpenAPI(__name__, info=info, security_schemes=security_schemes)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'oa;shdpoignqopweh'

# 定义标签
auth_tag = Tag(name="用户认证", description="用户认证相关操作")
user_tag = Tag(name="用户管理", description="用户管理API")
org_tag = Tag(name="组织管理", description="组织管理API")
task_tag = Tag(name="任务管理", description="任务管理API")

# 用户管理API
@app.post("/users/create",
          tags=[user_tag],
          summary="创建用户",
          responses={"200": {"description": "用户创建成功"}})

def create_user(body: UserModel):
    """
    创建用户
    """
    try:
        # 检查用户名是否已存在
        if dao.check_user_exists(body.username):
            logger.error(f"添加用户时用户名{body.username}已存在")
            return jsonify({"message": "用户名已存在"}), 400

        # 使用参数化查询防止 SQL 注入
        u_id = dao.add_user(body.username, body.password)
        if u_id is None:
            return jsonify({"message": "添加用户失败"}), 500
        
        # 默认设置普通用户角色
        role_id = dao.get_role_id_by_name('user')  # 获取角色ID
        if role_id is None:
            delete_user(u_id)  # 如果角色不存在，删除用户并返回错误
            logger.error("添加用户时角色不存在")
            return jsonify({"message": "添加用户失败"}), 400
        dao.assign_user_role(u_id, role_id)
        return jsonify({"message": "用户添加成功", "u_id": u_id}), 201
    except Exception as e:
        logger.error(f"添加用户时发生错误: {e}")
        return jsonify({"message": "添加用户失败", "error": str(e)}), 500

@app.post('/users/login',
          tags=[auth_tag],
          summary="获取JWT Token",
          responses={"200": {"description": "获取JWT Token成功"}})
def user_login(body: LoginModel):
    """
    用户认证
    """
    try:
        user = dao.user_login(body.username, body.password)
        if user:
            # 获取用户的u_id，并赋值给具有明确意义的局部变量
            user_id = user[0]
            logger.info(f"User found with user_id: {user_id}")
            # 获取用户的角色信息
            role_info = dao.get_user_role(user_id)
            if role_info:
                # access_token = create_access_token(identity=user_id, additional_claims={'role_id': role_info['role_id'], 'role_name': role_info['role_name']})
                token_info = {
                    "user_id": user_id,
                    "username": body.username,
                    "role_id": role_info['role_id'],
                    "role_name": role_info['role_name']
                }
                access_token = create_access_token(identity=f'{user_id}', additional_claims=token_info)
                data = {
                    "user_id": user_id,
                    "username": body.username,
                    "role_name": role_info['role_name']
                }
                return jsonify({"message": "Login successful", "access_token": access_token, "data": data},), 200
            else:
                return jsonify({"message": "User role not found"}), 401
        else:
            return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        logger.error(f"用户登录时发生错误: {e}")
        return jsonify({"message": "登录失败", "error": str(e)}), 500

# 删除用户
@app.delete("/users/<int:u_id>/delete",
            tags=[user_tag],
            summary="删除用户",
            responses={"200": {"description": "用户删除成功"}},
            security=security)
@jwt_required()
def delete_user(path: UserPath):
    """
    删除用户
    """
    try:
        print(path)
        u_id = path.u_id
        # 获取当前登录用户的ID
        current_user_id = get_jwt_identity()
        # 只有用户自己可以删除自己
        if current_user_id != f'{u_id}':
            return jsonify({"message": "无权删除该用户"}), 403

        # 删除用户
        rows_affected = dao.delete_user(u_id)
        if rows_affected > 0:
            return jsonify({"message": "User deleted successfully"}), 200
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        logger.error(f"删除用户时发生错误: {e}")
        return jsonify({"message": "删除用户失败", "error": str(e)}), 500

# 修改用户名
@app.put('/users/<int:u_id>/username',
            tags=[user_tag],
            summary="修改用户名",
            responses={"200": {"description": "用户名修改成功"}},
            security=security)
@jwt_required()
def update_user_name(path: UserPath, body: UserNameModel):
    """
    用户信息修改
    """
    try:
        u_id = path.u_id
        # 获取当前登录用户的ID
        current_user_id = get_jwt_identity()
        # 只有用户自己可以修改自己的信息
        if current_user_id != f'{u_id}':
            return jsonify({"message": "无权修改该用户信息"}), 403

        new_username = body.username

        # 在业务逻辑层检查新用户名是否已存在
        if new_username and dao.check_user_exists(new_username):
            return jsonify({"message": "用户名已存在"}), 400

        rows_affected = dao.update_user(u_id, new_username)
        if rows_affected > 0:
            return jsonify({"message": "User updated successfully"}), 200
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        logger.error(f"更新用户时发生错误: {e}")
        return jsonify({"message": "更新用户失败", "error": str(e)}), 500

# 修改用户密码
@app.put('/users/<int:u_id>/password',
         tags=[user_tag],
        summary="修改用户密码",
        responses={"200": {"description": "用户密码修改成功"}},
        security=security)
@jwt_required()
def update_user_password(path: UserPath, body: UserPasswordModel):
    """
    用户信息修改
    """
    try:
        u_id = path.u_id
        # 获取当前登录用户的ID
        current_user_id = int(get_jwt_identity())
        # 只有用户自己可以修改自己的信息
        if current_user_id != u_id:
            return jsonify({"message": "无权修改该用户信息"}), 403

        new_password = body.password
        rows_affected = dao.update_user_password(u_id, new_password)
        if rows_affected > 0:
            return jsonify({"message": "User password updated successfully"}), 200
        else:
            return jsonify({"message": "User password update fail"}), 404
    except Exception as e:
        logger.error(f"更新用户时发生错误: {e}")
        return jsonify({"message": "更新用户密码失败", "error": str(e)}), 500

# Get用户信息
@app.get('/users/<int:u_id>/info',
        tags=[user_tag],
        summary="获取用户信息",
        responses={"200": {"description": "用户信息获取成功"}},
        security=security)
@jwt_required()
def get_user_info(path: UserPath):
    """
    获取用户信息
    """
    try:
        u_id = path.u_id
        
        # 获取当前登录用户的ID
        current_user_id = int(get_jwt_identity())
        # 获取自己的信息可获得全量信息，非自己的信息只能获取部分信息
        if current_user_id!= u_id:
            # 获取用户基本信息
            user_info = dao.get_user_base_info(u_id)
        else:
            # 获取用户全量信息
            user_info = dao.get_user_all_info(u_id)
        logger.debug(user_info)
        
        if user_info:
            return jsonify({"message": "User info get successfully", "user_info": user_info}), 200
        else:
            return jsonify({"message": "User info get fail"}), 404
    except Exception as e:
        logger.error(f"获取用户信息时发生错误: {e}")
        return jsonify({"message": "获取用户信息失败", "error": str(e)}), 500

# 根据用户名查询用户信息
@app.get('/users/<string:username>/info',
        tags=[user_tag],
        summary="根据用户名查询用户信息",
        responses={"200": {"description": "用户信息获取成功"}},
        security=security)
@jwt_required()
def get_user_info_by_name(path: UserNameModel):
    """
    获取用户信息
    """
    try:
        username = path.username
        # 查找用户
        user_info = dao.get_user_info_by_name(username)
        logger.debug(user_info)
        if user_info:
            return jsonify({"message": "User info get successfully", "user_info": user_info}), 200
        else:
            return jsonify({"message": "User info get fail"}), 404
    except Exception as e:
        logger.error(f"获取用户信息时发生错误: {e}")
        return jsonify({"message": "获取用户信息失败", "error": str(e)}), 500

# 组织管理API
@app.post('/organizations/create',
         tags=[org_tag],
        summary="创建组织",
        responses={"201": {"description": "组织创建成功"}},
        security=security)
@jwt_required()
def create_organization(body: OrganizationModel):
    """
    增加组织
    """
    try:
        # 获取当前登录用户的ID，即组织的创建者ID
        creator_id = get_jwt_identity()

        # 检查组织名是否已存在
        if dao.check_organization_exists(body.c_name):
            return jsonify({"message": "组织名已存在"}), 400

        # 生成随机邀请码
        invite_code = generate_invite_code()

        # 校验类型是否有效
        if not cfg.is_org_type_valid(body.c_type):
            return jsonify({"message": "无效的组织类型"}), 400

        # 使用参数化查询防止 SQL 注入
        c_id = dao.add_organization(body.c_name, body.c_type, creator_id, invite_code)

        # 自动将创建者加入组织
        dao.add_user_to_organization(creator_id, c_id)

        return jsonify({"message": "Organization created successfully", "c_id": c_id, "invite_code": invite_code}), 201
    except Exception as e:
        logger.error(f"添加组织时发生错误: {e}")
        return jsonify({"message": "添加组织失败", "error": str(e)}), 500

@app.delete('/organizations/<int:c_id>/delete',
            tags=[org_tag],
            summary="删除组织",
            responses={"200": {"description": "组织删除成功"}},
            security=security)
@jwt_required()
def delete_organization(path: OrgPath):
    """
    删除组织
    """
    try:
        c_id = path.c_id
        # 获取当前登录用户的ID
        current_user_id = get_jwt_identity()

        # 检查当前用户是否为组织的创建者
        if not dao.is_organization_creator(c_id, current_user_id):
            return jsonify({"message": "只有组织的创建者才能删除该组织"}), 403

        rows_affected = dao.delete_organization(c_id)
        if rows_affected > 0:
            return jsonify({"message": "Organization deleted successfully"}), 200
        else:
            return jsonify({"message": "Organization not found"}), 404
    except Exception as e:
        logger.error(f"删除组织时发生错误: {e}")
        return jsonify({"message": "删除组织失败", "error": str(e)}), 500

@app.put('/organizations/<int:c_id>/join',
        tags=[org_tag],
        summary="加入组织",
        responses={"200": {"description": "组织加入成功"}},
        security=security)
@jwt_required()
def join_organization(path: OrgPath,body: OrganizationModel):
    """
    加入组织
    """
    try:
        user_id = int(get_jwt_identity())
        org_id = path.c_id
        invite_code = body.invite_code

        if not org_id or not invite_code:
            return jsonify({"message": "组织ID和邀请码不能为空"}), 400

        # 校验组织是否存在
        org_info = dao.get_organization(org_id)
        if not org_info:
            return jsonify({"message": "组织不存在"}), 404

        # 校验邀请码是否匹配
        if org_info['invite_code'] != invite_code:
            return jsonify({"message": "邀请码不匹配"}), 403

        # 校验用户是否已经加入该组织
        if dao.is_user_in_organization(user_id, org_id):
            return jsonify({"message": "用户已经加入该组织"}), 409

        # 加入组织
        dao.add_user_to_organization(user_id, org_id)
        return jsonify({"message": "成功加入组织", "organization": org_info}), 200
    except Exception as e:
        logger.error(f"user:{user_id}加入组织{org_id}时发生错误: {e}")
        return jsonify({"message": "加入组织失败", "error": str(e)}), 500

@app.put('/organizations/<int:c_id>/leave',
        tags=[org_tag],
        summary="离开组织",
        responses={"200": {"description": "组织离开成功"}},
        security=security)
@jwt_required()
def leave_organization(path: OrgPath):
    """
    离开组织
    """
    try:
        user_id = get_jwt_identity()
        org_id = path.c_id
        if not org_id:
            return jsonify({"message": "组织ID不能为空"}), 400

        # 校验组织是否存在
        org_info = dao.get_organization(org_id)
        if not org_info:
            return jsonify({"message": "组织不存在"}), 404

        # 校验用户是否在该组织
        if not dao.is_user_in_organization(user_id, org_id):
            return jsonify({"message": "用户不属于该组织"}), 403

        # 离开组织
        dao.remove_user_from_organization(user_id, org_id)
        return jsonify({"message": "成功离开组织", "organization": org_info}), 200

    except Exception as e:
        logger.error(f"user:{user_id}离开组织{org_id}时发生错误: {e}")
        return jsonify({"message": "离开组织失败", "error": str(e)}), 500

# Get组织信息
@app.get('/organizations/<int:c_id>/info',
         tags=[org_tag],
         summary="获取组织信息",
         responses={"200": {"description": "组织信息获取成功"}},
         security=security)
@jwt_required()
def get_organization_info(path: OrgPath):
    """
    获取组织信息
    """
    try:
        c_id = path.c_id
        
        # 非组织成员无法获取
        u_id = int(get_jwt_identity())
        if not dao.is_user_in_organization(u_id, c_id):
            return jsonify({"message": "无权限"}), 403
            
        # 获取组织信息
        org_info = dao.get_organization(c_id)
        if org_info:
            return jsonify({"message": "OK", "org_info": org_info}), 200
        else:
            return jsonify({"message": "获取组织信息失败"}), 404
    except Exception as e:
        logger.error(f"获取组织信息时发生错误: {e}")
        return jsonify({"message": "获取组织信息失败", "error": str(e)}), 500

# 任务管理API
# 发布任务
@app.put('/tasks/publish',
         tags=[task_tag],
         summary="发布任务",
         responses={"200": {"description": "任务发布成功"}},
         security=security)
@jwt_required()
def publish_task(body: TaskModel):
    """
    发布任务
    """
    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        # 检查用户是否为组织成员
        if not dao.is_user_in_organization(user_id, body.c_id):
            return jsonify({"message": "只有组织成员才能发布任务"}), 403

        # 默认接收者为空
        receiver_id = None

        # 获取任务状态配置
        config = cfg.get_config()
        task_status = config['task_status']['pending']

        task_id = dao.publish_task(body.task_name, body.publisher_id, receiver_id, task_status, body.time_limit, body.c_id, body.task_desc)
        return jsonify({"message": "Task published successfully", "task_id": task_id}), 201
    except Exception as e:
        logger.error(f"发布任务时发生错误: {e}")
        return jsonify({"message": "发布任务失败", "error": str(e)}), 500

# 接取任务
@app.put('/tasks/<int:task_id>/accept',
         tags=[task_tag],
         summary="接受任务",
         responses={"200": {"description": "任务接受成功"}},
         security=security)
@jwt_required()
def accept_task(path: TaskPath):
    """
    接取任务
    """
    try:
        user_id = get_jwt_identity()
        task_id = path.task_id
        # 检查用户是否为组织成员
        print(user_id, task_id)
        org_id = dao.get_organization_id_by_task_id(task_id)
        if not dao.is_user_in_organization(user_id, org_id):
            return jsonify({"message": "只有任务归属组织的成员才能接取任务"}), 403
    
        # 获取任务状态配置
        config = cfg.get_config()
    
        # 检查任务状态是否为待接取
        if dao.get_task_status(task_id) != config['task_status']['pending']:
            return jsonify({"message": "只有待接取的任务才能被接取"}), 400
    
        # 更新任务状态为进行中，并更新任务接收者
        rows_affected = dao.update_task_status_and_receiver(task_id, config['task_status']['in_progress'], user_id)
        if rows_affected > 0:
            return jsonify({"message": "Task accepted successfully"}), 200
        else:
            return jsonify({"message": "Task not found"}), 404
    except Exception as e:
        logger.error(f"接取任务时发生错误: {e}")
        return jsonify({"message": "接取任务失败", "error": str(e)}), 500
    
# 放弃任务
@app.put('/tasks/<int:task_id>/abandon',
        tags=[task_tag],
         summary="放弃任务",
         responses={"200": {"description": "任务放弃成功"}},
         security=security)
@jwt_required()
def abandon_task(path: TaskPath):
    """
    放弃任务
    """
    try:
        user_id = int(get_jwt_identity())
        task_id = path.task_id
        # 检查用户是否为任务的接收者
        receiver_id = dao.get_task_by_id(task_id).get('receiver_id')
        logger.debug(f"receiver_id:{receiver_id}, user_id:{user_id}")
        if user_id != receiver_id:
            return jsonify({"message": "只有任务的接收者才能放弃任务"}), 403
    
        # 获取任务状态配置
        config = cfg.get_config()
        # 检查任务状态是否为进行中或已过期
        task_status = dao.get_task_status(task_id)
        if task_status not in [config['task_status']['in_progress'], config['task_status']['expired']]:
            return jsonify({"message": "只有进行中或已过期的任务才能被放弃"}), 400
    
        # 更新任务状态为放弃
        rows_affected = dao.update_task_status(task_id, config['task_status']['abandoned'])
        if rows_affected > 0:
            return jsonify({"message": "Task abandoned successfully"}), 200
        else:
            return jsonify({"message": "Task not found"}), 404
    except Exception as e:
        logger.error(f"放弃任务时发生错误: {e}")
        return jsonify({"message": "放弃任务失败", "error": str(e)}), 500

# 提交任务
@app.put('/tasks/<int:task_id>/submit',
        tags=[task_tag],
        summary="提交任务",
        responses={"200": {"description": "任务提交成功"}},
        security=security)
@jwt_required()
def submit_task(path: TaskPath):
    """
    提交任务
    """
    try:
        user_id = int(get_jwt_identity())
        task_id = path.task_id
        # 检查用户是否为任务的接收者
        receiver_id = dao.get_task_by_id(task_id).get('receiver_id')
        logger.debug(f"receiver_id:{receiver_id}, user_id:{user_id}")
        if user_id != receiver_id:
            return jsonify({"message": "只有任务的接收者才能提交任务"}), 403

        # 获取任务状态配置
        config = cfg.get_config()

        # 检查任务状态是否为进行中
        if dao.get_task_status(task_id) != config['task_status']['in_progress']:
            return jsonify({"message": "只有进行中的任务才能被提交"}), 400

        # 更新任务状态为待确认
        rows_affected = dao.update_task_status(task_id, config['task_status']['to_be_confirmed'])
        if rows_affected > 0:
            return jsonify({"message": "Task submitted successfully"}), 200
        else:
            return jsonify({"message": "Task not found"}), 404
    except Exception as e:
        logger.error(f"提交任务时发生错误: {e}")
        return jsonify({"message": "提交任务失败", "error": str(e)}), 500
    
# 确认任务
@app.put('/tasks/<int:task_id>/confirm',
        tags=[task_tag],
        summary="确认任务",
        responses={"200": {"description": "任务确认成功"}},
        security=security)
@jwt_required()
def confirm_task(path: TaskPath):
    """
    确认任务
    """
    try:
        user_id = int(get_jwt_identity())
        task_id = path.task_id
        # 检查用户是否为任务的发布者
        publisher_id = dao.get_task_by_id(task_id).get('publisher_id')
        logger.debug(f"publisher_id:{publisher_id}, user_id:{user_id}")
        if user_id != publisher_id:
            return jsonify({"message": "只有任务的发布者才能确认任务"}), 403
    
        # 获取任务状态配置
        config = cfg.get_config()
    
        # 检查任务状态是否为待确认
        if dao.get_task_status(task_id) != config.get('task_status').get('to_be_confirmed'):
            return jsonify({"message": "只有待确认的任务才能被确认"}), 400
    
        # 确认任务
        rows_affected = dao.update_task_status(task_id, config.get('task_status').get('completed'))
        if rows_affected > 0:
            return jsonify({"message": f"Task confirmed successfully"}), 200
        else:
            return jsonify({"message": "Task not found"}), 404
    except Exception as e:
        logger.error(f"确认任务时发生错误: {e}")
        return jsonify({"message": "确认任务失败", "error": str(e)}), 500

# 删除任务
@app.delete('/tasks/<int:task_id>/delete',
            tags=[task_tag],
            summary="删除任务",
            responses={"200": {"description": "任务删除成功"}},
            security=security)
@jwt_required()
def delete_task(path: TaskPath):
    """
    删除任务
    """
    try:
        user_id = int(get_jwt_identity())
        task_id = path.task_id
        
        task = dao.get_task_by_id(task_id)
        # 检查任务存在
        if not task:
            return jsonify({"message": "Task not found"}), 404

        # 检查用户是否为任务的发布者
        publisher_id = task.get('publisher_id')
        logger.debug(f"publisher_id:{publisher_id}, user_id:{user_id}")
        if user_id!= publisher_id:
            return jsonify({"message": "只有任务的发布者才能删除任务"}), 403


        
        # 删除任务
        rows_affected = dao.delete_task(task_id)
        if rows_affected > 0:
            return jsonify({"message": "Task deleted successfully"}), 200
        else:
            return jsonify({"message": "Task not found"}), 404
    except Exception as e:
        logger.error(f"删除任务时发生错误: {e}")
        return jsonify({"message": "删除任务失败", "error": str(e)}), 500


# 全局错误处理
@app.errorhandler(Exception)
def handle_error(e):
    logger.error(f"发生未处理的异常: {e}")
    return jsonify({"message": "服务器内部错误", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)