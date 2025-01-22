import mysql.connector
import json
from logger import LoggerFactory

logger = LoggerFactory.getLogger()

class EarthFighterDAO:
    def __init__(self):
        with open('config/db_config.json') as config_file:
            config = json.load(config_file)
        try:
            self.db = mysql.connector.connect(
                host=config['host'],
                user=config['user'],
                password=config['password'],
                database=config['database']
            )
            self.cursor = self.db.cursor()
        except mysql.connector.Error as err:
            logger.error(f"Error connecting to MySQL database: {err}")
            raise

    def check_user_exists(self, u_name):
        """
        检查用户名是否已存在
        """
        sql_check = "SELECT u_id FROM users WHERE u_name = %s AND is_deleted = FALSE"
        val_check = (u_name,)
        self.cursor.execute(sql_check, val_check)
        existing_user = self.cursor.fetchone()
        return existing_user is not None

    def add_user(self, u_name, password):
        sql_insert = "INSERT INTO users (u_name, password, register_time) VALUES (%s, %s, NOW())"
        val_insert = (u_name, password)
        try:
            self.cursor.execute(sql_insert, val_insert)
            self.db.commit()
            return self.cursor.lastrowid
        except mysql.connector.Error as err:
            logger.error(f"Error adding user: {err}")
            self.db.rollback()
            raise
    def delete_user(self, u_id):
        sql = "UPDATE users SET is_deleted = TRUE WHERE u_id = %s"
        val = (u_id,)
        try:
            self.cursor.execute(sql, val)
            self.db.commit()
            return self.cursor.rowcount
        except mysql.connector.Error as err:
            logger.error(f"Error deleting user: {err}")
            self.db.rollback()
            raise

    def update_user(self, u_id, u_name):
        sql = "UPDATE users SET u_name = %s WHERE u_id = %s"
        val = (u_name, u_id)
        try:
            self.cursor.execute(sql, val)
            self.db.commit()
            return self.cursor.rowcount
        except mysql.connector.Error as err:
            logger.error(f"Error updating user: {err}")
            self.db.rollback()
            raise

    def update_user_password(self, u_id, password):
        sql = "UPDATE users SET password = %s WHERE u_id = %s"
        val = (password, u_id)
        try:
            self.cursor.execute(sql, val)
            self.db.commit()
            return self.cursor.rowcount
        except mysql.connector.Error as err:
            logger.error(f"Error updating user password: {err}")
            self.db.rollback()
            raise

    def get_role_id_by_name(self, role_name):
        """
        根据角色名称获取角色ID
        """
        sql = "SELECT role_id FROM roles WHERE role_name = %s"
        val = (role_name,)
        try:
            self.cursor.execute(sql, val)
            role_info = self.cursor.fetchone()
            return role_info[0] if role_info else None
        except mysql.connector.Error as err:
            logger.error(f"Error getting role ID: {err}")
            raise
    def update_user_role(self, u_id, role_id):
        """
        更新用户的角色信息
        """
        sql = "UPDATE user_role SET role_id = %s WHERE user_id = %s"
        val = (role_id, u_id)
        try:
            self.cursor.execute(sql, val)
            self.db.commit()
            return self.cursor.rowcount
        except mysql.connector.Error as err:
            logger.error(f"Error updating user role: {err}")
            self.db.rollback()
            raise
    def assign_user_role(self, u_id, role_id):
        """
        为用户分配角色
        """
        sql = "INSERT INTO user_role (user_id, role_id) VALUES (%s, %s)"
        val = (u_id, role_id)
        try:
            self.cursor.execute(sql, val)
            self.db.commit()
            return self.cursor.rowcount
        except mysql.connector.Error as err:
            logger.error(f"Error assigning user role: {err}")
            self.db.rollback()
            raise
    def user_login(self, u_name, password):
        sql = "SELECT * FROM users WHERE u_name = %s AND password = %s AND is_deleted = FALSE"
        val = (u_name, password)
        try:
            self.cursor.execute(sql, val)
            user = self.cursor.fetchone()
            return user
        except mysql.connector.Error as err:
            logger.error(f"Error during user login: {err}")
            raise
    def get_user_role(self, u_id):
        """
        获取用户的角色信息
        """
        sql = "SELECT roles.role_id, roles.role_name FROM roles JOIN user_role ON roles.role_id = user_role.role_id WHERE user_role.user_id = %s"
        val = (u_id,)
        self.cursor.execute(sql, val)
        role_info = self.cursor.fetchone()
        return {'role_id': role_info[0], 'role_name': role_info[1]} if role_info else None

    def check_organization_exists(self, c_name):
        """
        检查组织是否已存在
        """
        sql_check = "SELECT c_id FROM organizations WHERE c_name = %s AND is_deleted = FALSE"
        val_check = (c_name,)
        self.cursor.execute(sql_check, val_check)
        existing_org = self.cursor.fetchone()
        return existing_org is not None

    def add_organization(self, c_name, c_type, creator_id, invite_code):
        sql = "INSERT INTO organizations (c_name, c_type, creator_id, invite_code, is_deleted) VALUES (%s, %s, %s, %s, FALSE)"
        val = (c_name, c_type, creator_id, invite_code)
        try:
            self.cursor.execute(sql, val)
            self.db.commit()
            return self.cursor.lastrowid
        except mysql.connector.Error as err:
            logger.error(f"Error adding organization: {err}")
            self.db.rollback()
            raise

    def delete_organization(self, c_id):
        sql = "UPDATE organizations SET is_deleted = TRUE WHERE c_id = %s"
        val = (c_id,)
        try:
            self.cursor.execute(sql, val)
            self.db.commit()
            return self.cursor.rowcount
        except mysql.connector.Error as err:
            logger.error(f"Error deleting organization: {err}")
            self.db.rollback()
            raise
    def add_user_to_organization(self, user_id, organization_id):
        """
        将用户添加到组织
        """
        sql = "INSERT INTO user_org_relations (u_id, c_id) VALUES (%s, %s)"
        val = (user_id, organization_id)
        try:
            self.cursor.execute(sql, val)
            self.db.commit()
        except mysql.connector.Error as err:
            logger.error(f"Error adding user to organization: {err}")
            self.db.rollback()
            raise

    def remove_user_from_organization(self, user_id, organization_id):
        """
        从组织中移除用户
        """
        sql = "DELETE FROM user_org_relations WHERE u_id = %s AND c_id = %s"
        val = (user_id, organization_id)
        try:
            self.cursor.execute(sql, val)
            self.db.commit()
        except mysql.connector.Error as err:
            logger.error(f"Error removing user from organization: {err}")
            self.db.rollback()
            raise
        
    def publish_task(self, task_name, publisher_id, receiver_id, task_state, time_limit, c_id, task_desc):
        sql = """
                INSERT INTO tasks (task_name, publisher_id, receiver_id, task_state, publish_time, time_limit, c_id, task_desc) 
                 VALUES (%s, %s, %s, %s, NOW(), %s, %s, %s)
              """
        val = (task_name, publisher_id, receiver_id, task_state, time_limit, c_id, task_desc)
        try:
            self.cursor.execute(sql, val)
            self.db.commit()
            return self.cursor.lastrowid
        except mysql.connector.Error as err:
            logger.error(f"Error publishing task: {err}")
            self.db.rollback()
            raise
    def get_task_status(self, task_id):
        """
        获取任务状态
        """
        try:
            sql = "SELECT task_state FROM tasks WHERE task_id = %s"
            val = (task_id,)
            self.cursor.execute(sql, val)
            result = self.cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
        except mysql.connector.Error as err:
            logger.error(f"获取任务状态时发生错误: {err}")
            raise
    def update_task_status(self, task_id, task_status):
        """
        更新任务状态
        """
        try:
            sql = "UPDATE tasks SET task_state = %s WHERE task_id = %s"
            val = (task_status, task_id)
            self.cursor.execute(sql, val)
            self.db.commit()
            return self.cursor.rowcount
        except mysql.connector.Error as err:
            logger.error(f"更新任务状态时发生错误: {err}")
            self.db.rollback()
            raise
    def update_task_status_and_receiver(self, task_id, task_status, receiver_id):
        """
        更新任务状态和接收者
        """
        try:
            sql = "UPDATE tasks SET task_state = %s, receiver_id = %s WHERE task_id = %s"
            val = (task_status, receiver_id, task_id)
            self.cursor.execute(sql, val)
            self.db.commit()
            return self.cursor.rowcount
        except mysql.connector.Error as err:
            logger.error(f"更新任务状态和接收者时发生错误: {err}")
            self.db.rollback()
            raise
    def is_organization_creator(self, organization_id, user_id):
        """
        检查用户是否为组织的创建者
        """
        sql = "SELECT COUNT(*) FROM organizations WHERE c_id = %s AND creator_id = %s"
        val = (organization_id, user_id)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchone()
        return result[0] > 0
    def is_user_in_organization(self, user_id, organization_id):
        """
        检查用户是否为组织成员
        """
        sql = "SELECT COUNT(*) FROM user_org_relations WHERE u_id = %s AND c_id = %s"
        val = (user_id, organization_id)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchone()
        return result[0] > 0
    
    def get_organization(self, c_id):
        """
        获取组织信息
        """
        try:
            sql = "SELECT * FROM organizations WHERE c_id = %s"
            val = (c_id,)
            self.cursor.execute(sql, val)
            result = self.cursor.fetchone()
            logger.debug(f"{__name__}查询结果: {result}")
            if result:
                return {
                    "c_id": result[0],
                    "c_name": result[1],
                    "c_type": result[2],
                    "creator_id": result[3],
                    "invite_code": result[4],
                    "create_time": result[5],
                    "is_deleted": result[6]
                }
            else:
                return None
        except mysql.connector.Error as err:
            logger.error(f"获取组织信息时发生错误: {err}")
            raise

    def get_organization_id_by_task_id(self, task_id):
        """
        根据任务ID获取组织ID
        """
        try:
            sql = "SELECT c_id FROM tasks WHERE task_id = %s"
            val = (task_id,)
            self.cursor.execute(sql, val)
            result = self.cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
        except mysql.connector.Error as err:
            logger.error(f"获取组织ID时发生错误: {err}")
            raise
    
    def get_task_by_id(self, task_id):
        """
        根据任务ID获取任务信息
        """
        try:
            sql = "SELECT * FROM tasks WHERE task_id = %s"
            val = (task_id,)
            self.cursor.execute(sql, val)
            result = self.cursor.fetchone()
            if result:
                logger.debug(f"{__name__}查询结果: {result}")
                return {
                    "task_id": result[0],
                    "task_name": result[1],        
                    "publisher_id": result[2],
                    "receiver_id": result[3],
                    "task_state": result[4],
                    "publish_time": result[5],
                    "time_limit": result[6],
                    "completion_time": result[7],
                    "c_id": result[9],
                    "task_desc": result[10]
                }
            else:
                return None
        except mysql.connector.Error as err:
            logger.error(f"获取任务信息时发生错误: {err}")
            raise

    def close(self):
        try:
            self.cursor.close()
            self.db.close()
        except mysql.connector.Error as err:
            logger.error(f"Error closing database connection: {err}")
            raise