from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from db_dao import EarthFighterDAO
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'kjsyhgjsudhkl6z.af-190sjklp30'  # 替换为你自己的密钥
jwt = JWTManager(app)
dao = EarthFighterDAO()

# 用户管理API
@app.route('/users', methods=['POST'])
def add_user():
    """
    增加用户
    """
    try:
        data = request.get_json()
        # 检查用户名是否已存在
        if dao.check_user_exists(data['u_name']):
            return jsonify({"message": "用户名已存在"}), 400

        # 使用参数化查询防止 SQL 注入
        u_id = dao.add_user(data['u_name'], data['password'])
        return jsonify({"message": "User added successfully", "u_id": u_id}), 201
    except Exception as e:
        logging.error(f"添加用户时发生错误: {e}")
        return jsonify({"message": "添加用户失败", "error": str(e)}), 500

@app.route('/users/<int:u_id>', methods=['DELETE'])
@jwt_required()
def delete_user(u_id):
    """
    删除用户
    """
    try:
        # 获取当前登录用户的ID
        current_user_id = get_jwt_identity()
        # 只有用户自己可以删除自己
        if current_user_id != u_id:
            return jsonify({"message": "无权删除该用户"}), 403

        # 删除用户
        rows_affected = dao.delete_user(u_id)
        if rows_affected > 0:
            return jsonify({"message": "User deleted successfully"}), 200
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        logging.error(f"删除用户时发生错误: {e}")
        return jsonify({"message": "删除用户失败", "error": str(e)}), 500

@app.route('/users/<int:u_id>', methods=['PUT'])
@jwt_required()
def update_user(u_id):
    """
    用户信息修改
    """
    try:
        # 获取当前登录用户的ID
        current_user_id = get_jwt_identity()
        # 只有用户自己可以修改自己的信息
        if current_user_id != u_id:
            return jsonify({"message": "无权修改该用户信息"}), 403

        data = request.get_json()
        new_username = data.get('u_name')

        # 在业务逻辑层检查新用户名是否已存在
        if new_username and dao.check_user_exists(new_username):
            return jsonify({"message": "用户名已存在"}), 400

        rows_affected = dao.update_user(u_id, new_username, data.get('password'))
        if rows_affected > 0:
            return jsonify({"message": "User updated successfully"}), 200
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        logging.error(f"更新用户时发生错误: {e}")
        return jsonify({"message": "更新用户失败", "error": str(e)}), 500
@app.route('/users/login', methods=['POST'])
def user_login():
    """
    用户认证
    """
    try:
        data = request.get_json()
        user = dao.user_login(data['u_name'], data['password'])
        if user:
            # 获取用户的u_id，并赋值给具有明确意义的局部变量
            user_id = user[0]
            logging.info(f"User found with user_id: {user_id}")
            # 获取用户的角色信息
            role_info = dao.get_user_role(user_id)
            if role_info:
                access_token = create_access_token(identity=user_id, additional_claims={'role_id': role_info['role_id'], 'role_name': role_info['role_name']})
                return jsonify({"message": "Login successful", "access_token": access_token}), 200
            else:
                return jsonify({"message": "User role not found"}), 401
        else:
            return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        logging.error(f"用户登录时发生错误: {e}")
        return jsonify({"message": "登录失败", "error": str(e)}), 500

# 组织管理API
import random
import string

def generate_invite_code():
    """
    生成随机的6位大小写字母组合的邀请码
    """
    return ''.join(random.choices(string.ascii_letters, k=6))

@app.route('/organizations', methods=['POST'])
@jwt_required()
def add_organization():
    """
    增加组织
    """
    try:
        data = request.get_json()
        # 获取当前登录用户的ID，即组织的创建者ID
        creator_id = get_jwt_identity()

        # 检查组织名是否已存在
        if dao.check_organization_exists(data['c_name']):
            return jsonify({"message": "组织名已存在"}), 400

        # 生成随机邀请码
        invite_code = generate_invite_code()

        # 使用参数化查询防止 SQL 注入
        c_id = dao.add_organization(data['c_name'], data['c_type'], creator_id, invite_code)

        # 自动将创建者加入组织
        dao.add_user_to_organization(creator_id, c_id)

        return jsonify({"message": "Organization added successfully", "c_id": c_id, "invite_code": invite_code}), 201
    except Exception as e:
        logging.error(f"添加组织时发生错误: {e}")
        return jsonify({"message": "添加组织失败", "error": str(e)}), 500

@app.route('/organizations/<int:c_id>', methods=['DELETE'])
@jwt_required()
def delete_organization(c_id):
    """
    删除组织
    """
    try:
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
        logging.error(f"删除组织时发生错误: {e}")
        return jsonify({"message": "删除组织失败", "error": str(e)}), 500

# 任务管理API
import json
from config_manager import ConfigManager

# 发布任务
@app.route('/tasks', methods=['POST'])
@jwt_required()
def publish_task():
    """
    发布任务
    """
    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        # 检查用户是否为组织成员
        if not dao.is_user_in_organization(user_id, data['c_id']):
            return jsonify({"message": "只有组织成员才能发布任务"}), 403

        # 默认接收者为空
        receiver_id = data.get('receiver_id', None)

        # 获取任务状态配置
        config_manager = ConfigManager()
        config = config_manager.get_config()
        task_status = config['task_status']['pending']

        task_id = dao.publish_task(data['publisher_id'], receiver_id, task_status, data['time_limit'], data['c_id'], data['task_desc'])
        return jsonify({"message": "Task published successfully", "task_id": task_id}), 201
    except Exception as e:
        logging.error(f"发布任务时发生错误: {e}")
        return jsonify({"message": "发布任务失败", "error": str(e)}), 500

# 接取任务
@app.route('/tasks/<int:task_id>/accept', methods=['PUT'])
@jwt_required()
def accept_task(task_id):
    """
    接取任务
    """
    try:
        user_id = get_jwt_identity()
    
        # 检查用户是否为组织成员
        if not dao.is_user_in_organization(user_id, dao.get_task_organization(task_id)):
            return jsonify({"message": "只有任务归属组织的成员才能接取任务"}), 403
    
        # 获取任务状态配置
        config_manager = ConfigManager()
        config = config_manager.get_config()
    
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
        logging.error(f"接取任务时发生错误: {e}")
        return jsonify({"message": "接取任务失败", "error": str(e)}), 500
    
# 放弃任务
@app.route('/tasks/<int:task_id>/abandon', methods=['PUT'])
@jwt_required()
def abandon_task(task_id):
    """
    放弃任务
    """
    try:
        user_id = get_jwt_identity()
    
        # 检查用户是否为任务的接收者
        if user_id != dao.get_task_receiver(task_id):
            return jsonify({"message": "只有任务的接收者才能放弃任务"}), 403
    
        # 获取任务状态配置
        config_manager = ConfigManager()
        config = config_manager.get_config()
    
        # 检查任务状态是否为进行中或已过期
        task_status = dao.get_task_status(task_id)
        if task_status not in [config['task_status']['in_progress'], config['task_status']['expired']]:
            return jsonify({"message": "只有进行中或已过期的任务才能被放弃"}), 400
    
        # 更新任务状态为放弃
        rows_affected = dao.update_task_status(task_id, config['task_status']['abandoned'])  # 假设放弃状态的值为7
        if rows_affected > 0:
            return jsonify({"message": "Task abandoned successfully"}), 200
        else:
            return jsonify({"message": "Task not found"}), 404
    except Exception as e:
        logging.error(f"放弃任务时发生错误: {e}")
        return jsonify({"message": "放弃任务失败", "error": str(e)}), 500
    
# 确认任务
@app.route('/tasks/<int:task_id>/confirm', methods=['PUT'])
@jwt_required()
def confirm_task(task_id):
    """
    确认任务
    """
    try:
        user_id = get_jwt_identity()
    
        # 检查用户是否为任务的发布者
        if user_id != dao.get_task_publisher(task_id):
            return jsonify({"message": "只有任务的发布者才能确认任务"}), 403
    
        # 获取任务状态配置
        config_manager = ConfigManager()
        config = config_manager.get_config()
    
        # 检查任务状态是否为待确认
        if dao.get_task_status(task_id) != config['task_status']['to_be_confirmed']:
            return jsonify({"message": "只有待确认的任务才能被确认"}), 400
    
        # 获取确认结果（成功或失败）
        confirm_result = request.json.get('confirm_result')
        if confirm_result not in ['success', 'failure']:
            return jsonify({"message": "确认结果必须为'success'或'failure'"}), 400
    
        # 更新任务状态为成功或失败
        task_status = config['task_status']['completed'] if confirm_result == 'success' else config['task_status']['failed']
        rows_affected = dao.update_task_status(task_id, task_status)
        if rows_affected > 0:
            return jsonify({"message": f"Task confirmed as {confirm_result} successfully"}), 200
        else:
            return jsonify({"message": "Task not found"}), 404
    except Exception as e:
        logging.error(f"确认任务时发生错误: {e}")
        return jsonify({"message": "确认任务失败", "error": str(e)}), 500

# 提交任务
@app.route('/tasks/<int:task_id>/submit', methods=['PUT'])
@jwt_required()
def submit_task(task_id):
    """
    提交任务
    """
    try:
        user_id = get_jwt_identity()

        # 检查用户是否为任务的接收者
        if user_id != dao.get_task_receiver(task_id):
            return jsonify({"message": "只有任务的接收者才能提交任务"}), 403

        # 获取任务状态配置
        config_manager = ConfigManager()
        config = config_manager.get_config()

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
        logging.error(f"提交任务时发生错误: {e}")
        return jsonify({"message": "提交任务失败", "error": str(e)}), 500

# 全局错误处理
@app.errorhandler(Exception)
def handle_error(e):
    logging.error(f"发生未处理的异常: {e}")
    return jsonify({"message": "服务器内部错误", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)