import mysql.connector
import json
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
            logging.error(f"Error connecting to MySQL database: {err}")
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
        # 直接插入新用户，不检查用户名是否已存在
        sql_insert = "INSERT INTO users (u_name, password, register_time) VALUES (%s, %s, NOW())"
        val_insert = (u_name, password)
        try:
            self.cursor.execute(sql_insert, val_insert)
            self.db.commit()
            return self.cursor.lastrowid
        except mysql.connector.Error as err:
            logging.error(f"Error adding user: {err}")
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
            logging.error(f"Error deleting user: {err}")
            self.db.rollback()
            raise

    def update_user(self, u_id, u_name, password):
        sql = "UPDATE users SET u_name = %s, password = %s WHERE u_id = %s"
        val = (u_name, password, u_id)
        try:
            self.cursor.execute(sql, val)
            self.db.commit()
            return self.cursor.rowcount
        except mysql.connector.Error as err:
            logging.error(f"Error updating user: {err}")
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
            logging.error(f"Error during user login: {err}")
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

    def add_organization(self, c_name, c_type):
        sql = "INSERT INTO organizations (c_name, c_type, is_deleted) VALUES (%s, %s, FALSE)"
        val = (c_name, c_type)
        try:
            self.cursor.execute(sql, val)
            self.db.commit()
            return self.cursor.lastrowid
        except mysql.connector.Error as err:
            logging.error(f"Error adding organization: {err}")
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
            logging.error(f"Error deleting organization: {err}")
            self.db.rollback()
            raise
    def add_user_to_organization(self, user_id, organization_id):
        """
        将用户添加到组织
        """
        sql = "INSERT INTO user_organization (user_id, organization_id) VALUES (%s, %s)"
        val = (user_id, organization_id)
        try:
            self.cursor.execute(sql, val)
            self.db.commit()
        except mysql.connector.Error as err:
            logging.error(f"Error adding user to organization: {err}")
            self.db.rollback()
            raise
    def publish_task(self, publisher_id, receiver_id, task_state, time_limit):
        sql = "INSERT INTO tasks (publisher_id, receiver_id, task_state, publish_time, time_limit) VALUES (%s, %s, %s, NOW(), %s)"
        val = (publisher_id, receiver_id, task_state, time_limit)
        try:
            self.cursor.execute(sql, val)
            self.db.commit()
            return self.cursor.lastrowid
        except mysql.connector.Error as err:
            logging.error(f"Error publishing task: {err}")
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
            logging.error(f"获取任务状态时发生错误: {err}")
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
            logging.error(f"更新任务状态时发生错误: {err}")
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
            logging.error(f"更新任务状态和接收者时发生错误: {err}")
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
        sql = "SELECT COUNT(*) FROM user_organization WHERE user_id = %s AND organization_id = %s"
        val = (user_id, organization_id)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchone()
        return result[0] > 0
    def close(self):
        try:
            self.cursor.close()
            self.db.close()
        except mysql.connector.Error as err:
            logging.error(f"Error closing database connection: {err}")
            raise