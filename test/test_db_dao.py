import unittest
import mysql.connector
import json
import sys
import os

# Add the parent directory of 'src' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..\src')))

# Now you can import from 'src'
from src.db_dao import EarthFighterDAO

class TestEarthFighterDAO(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('config/db_config.json') as config_file:
            config = json.load(config_file)
        cls.db = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
        cls.cursor = cls.db.cursor()
        cls.dao = EarthFighterDAO()

    @classmethod
    def tearDownClass(cls):
        cls.cursor.close()
        cls.db.close()

    def setUp(self):
        # 在每个测试方法运行前，清空相关表中的数据
        self.cursor.execute("DELETE FROM user_org_relations")
        self.cursor.execute("DELETE FROM user_role")
        self.cursor.execute("DELETE FROM tasks")
        self.cursor.execute("DELETE FROM organizations")
        self.cursor.execute("DELETE FROM users")
        # self.cursor.execute("DELETE FROM roles")
        self.db.commit()

    def test_add_user_succ(self):
        u_id = self.dao.add_user("test_user", "test_password")
        self.assertEqual(self.dao.check_user_exists('test_user'), True)
        self.cursor.execute("SELECT * FROM users WHERE u_id = %s", (u_id,))
        user = self.cursor.fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user[1], "test_user")
        self.assertEqual(user[2], "test_password")

    def test_add_user_fail(self):
        self.dao.add_user("test_user", "test_password")
        with self.assertRaises(mysql.connector.Error):
            self.dao.add_user("test_user", "test_password")

    def test_delete_user_succ(self):
        u_id = self.dao.add_user("test_user", "test_password")
        self.assertEqual(self.dao.check_user_exists('test_user'), True)
        rows_affected = self.dao.delete_user(u_id)
        self.assertEqual(rows_affected, 1)
        self.cursor.execute("SELECT is_deleted FROM users WHERE u_id = %s", (u_id,))
        is_deleted = self.cursor.fetchone()[0]
        self.assertEqual(is_deleted, 1)

    def test_delete_user_no_data(self):
        rows_affected = self.dao.delete_user(1)
        self.assertEqual(rows_affected, 0)

    def test_check_user_exists(self):
        self.dao.add_user("test_user", "test_password")
        self.assertEqual(self.dao.check_user_exists('test_user'), True)
        self.assertEqual(self.dao.check_user_exists('nonexistent_user'), False)
    
    def test_get_role_id_by_name(self):
        role_id = self.dao.get_role_id_by_name("admin")
        self.assertIsNotNone(role_id)

    def test_update_user_role(self):
        u_id = self.dao.add_user("test_user", "test_password")
        role_id = self.dao.get_role_id_by_name("admin")
        rows_affected = self.dao.assign_user_role(u_id, role_id)
        self.assertEqual(rows_affected, 1)
        self.assertEqual(self.dao.get_user_role(u_id)['role_id'], role_id)

        role_id = self.dao.get_role_id_by_name("user")
        rows_affected = self.dao.update_user_role(u_id, role_id)
        self.assertEqual(rows_affected, 1)
        self.assertEqual(self.dao.get_user_role(u_id)['role_id'], role_id)

    def test_get_user_role(self):
        u_id = self.dao.add_user("test_user", "test_password")
        role_id = self.dao.get_role_id_by_name("admin")
        self.dao.assign_user_role(u_id, role_id)
        role_info = self.dao.get_user_role(u_id)
        self.assertIsNotNone(role_info)
        self.assertEqual(role_info['role_id'], role_id)
        self.assertEqual(role_info['role_name'], "admin")

    def test_update_user(self):
        u_id = self.dao.add_user("test_user", "test_password")
        rows_affected = self.dao.update_user(u_id, "updated_user")
        self.assertEqual(rows_affected, 1)
        self.cursor.execute("SELECT * FROM users WHERE u_id = %s", (u_id,))
        user = self.cursor.fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user[1], "updated_user")

    def test_update_user_password(self):
        u_id = self.dao.add_user("test_user", "test_password")
        rows_affected = self.dao.update_user_password(u_id, "updated_password")
        self.assertEqual(rows_affected, 1)
        self.cursor.execute("SELECT * FROM users WHERE u_id = %s", (u_id,))
        user = self.cursor.fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user[2], "updated_password")

    def test_user_login(self):
        self.dao.add_user("test_user", "test_password")
        user = self.dao.user_login("test_user", "test_password")
        self.assertIsNotNone(user)
        self.assertEqual(user[1], "test_user")
        self.assertEqual(user[2], "test_password")

    def test_add_organization(self):
        u_id = self.dao.add_user("test_user", "test_password")
        c_id = self.dao.add_organization("test_org", "test_type", u_id, "test_invite_code")
        self.cursor.execute("SELECT * FROM organizations WHERE c_id = %s", (c_id,))
        org = self.cursor.fetchone()
        self.assertIsNotNone(org)
        self.assertEqual(org[1], "test_org")
        self.assertEqual(org[2], "test_type")

    def test_delete_organization(self):
        u_id = self.dao.add_user("test_user", "test_password")
        c_id = self.dao.add_organization("test_org", "test_type", u_id, "test_invite_code")
        rows_affected = self.dao.delete_organization(c_id)
        self.assertEqual(rows_affected, 1)
        self.cursor.execute("SELECT is_deleted FROM organizations WHERE c_id = %s", (c_id,))
        is_deleted = self.cursor.fetchone()[0]
        self.assertEqual(is_deleted, 1)


    def test_publish_task(self):
        publisher_id = self.dao.add_user("publisher", "publisher_password")
        org_id = self.dao.add_organization("test_org", "test_type", publisher_id, "test_invite_code")
        task_id = self.dao.publish_task("task_name", publisher_id, None, 0, 3600, org_id, "task_desc")
        self.cursor.execute("SELECT * FROM tasks WHERE task_id = %s", (task_id,))
        task = self.cursor.fetchone()
        self.assertIsNotNone(task)
        self.assertEqual(task[1], "task_name")
        self.assertEqual(task[2], publisher_id)
        self.assertEqual(task[3], None)
        self.assertEqual(task[4], 0)

    def test_update_task_status(self):
        publisher_id = self.dao.add_user("publisher", "publisher_password")
        receiver_id = self.dao.add_user("receiver", "receiver_password")
        org_id = self.dao.add_organization("test_org", "test_type", publisher_id, "test_invite_code")
        task_id = self.dao.publish_task("task_name", publisher_id, None, 0, 3600, org_id, "task_desc")
        rows_affected = self.dao.update_task_status(task_id, 1)
        self.assertEqual(rows_affected, 1)        
        self.cursor.execute("SELECT * FROM tasks WHERE task_id = %s", (task_id,))
        task = self.cursor.fetchone()
        self.assertIsNotNone(task)
        self.assertEqual(task[4], 1)

    def test_receive_task(self):
        publisher_id = self.dao.add_user("publisher", "publisher_password")
        receiver_id = self.dao.add_user("receiver", "receiver_password")
        org_id = self.dao.add_organization("test_org", "test_type", publisher_id, "test_invite_code")
        task_id = self.dao.publish_task("task_name", publisher_id, None, 0, 3600, org_id, "task_desc")
        task_state = 1
        rows_affected = self.dao.update_task_status_and_receiver(task_id, task_state, receiver_id)
        self.assertEqual(rows_affected, 1)
        self.cursor.execute("SELECT * FROM tasks WHERE task_id = %s", (task_id,))
        task = self.cursor.fetchone()
        self.assertIsNotNone(task)
        self.assertEqual(task[4], task_state)
        self.assertEqual(task[3], receiver_id)

    def test_get_task_status(self):
        publisher_id = self.dao.add_user("publisher", "publisher_password")
        receiver_id = self.dao.add_user("receiver", "receiver_password")
        task_state = 0
        org_id = self.dao.add_organization("test_org", "test_type", publisher_id, "test_invite_code")
        task_id = self.dao.publish_task("task_name", publisher_id, None, 0, 3600, org_id, "task_desc")
        self.assertEqual(task_state, self.dao.get_task_status(task_id))

    def test_add_user_to_organization(self):
        u_id = self.dao.add_user("test_user", "test_password")
        c_id = self.dao.add_organization("test_org", "test_type", u_id, "test_invite_code")
        self.dao.add_user_to_organization(u_id, c_id)
        self.cursor.execute("SELECT * FROM user_org_relations WHERE u_id = %s AND c_id = %s", (u_id, c_id))
        relation = self.cursor.fetchone()
        self.assertIsNotNone(relation)

    def test_remove_user_from_organization(self):
        u_id = self.dao.add_user("test_user", "test_password")
        c_id = self.dao.add_organization("test_org", "test_type", u_id, "test_invite_code")
        self.dao.add_user_to_organization(u_id, c_id)
        self.dao.remove_user_from_organization(u_id, c_id)
        self.cursor.execute("SELECT * FROM user_org_relations WHERE u_id = %s AND c_id = %s", (u_id, c_id))
        relation = self.cursor.fetchone()
        self.assertIsNone(relation)
        
    def test_is_organization_creator(self):
        u_id = self.dao.add_user("test_user", "test_password")
        c_id = self.dao.add_organization("test_org", "test_type", u_id, "test_invite_code")
        self.assertTrue(self.dao.is_organization_creator(c_id, u_id))

    def test_is_user_in_organization(self):
        u_id = self.dao.add_user("test_user", "test_password")
        c_id = self.dao.add_organization("test_org", "test_type", u_id, "test_invite_code")
        self.dao.add_user_to_organization(u_id, c_id)
        self.assertTrue(self.dao.is_user_in_organization(u_id, c_id))

    def test_check_organization_exists(self):
        c_name = "test_org"
        self.assertFalse(self.dao.check_organization_exists(c_name))

        creater_id = self.dao.add_user("test_user", "test_password")
        self.dao.add_organization(c_name, "test_type", creater_id, "test_invite_code")
        self.assertTrue(self.dao.check_organization_exists(c_name))
    
    def test_get_organization(self):
        c_name = "test_org"
        creater_id = self.dao.add_user("test_user", "test_password")
        c_id = self.dao.add_organization(c_name, "test_type", creater_id, "test_invite_code")
        org = self.dao.get_organization(c_id)
        print(org)
        self.assertIsNotNone(org)
        self.assertEqual(org['c_name'], c_name)
        self.assertEqual(org['c_type'], "test_type")
        self.assertEqual(org['creator_id'], creater_id)
        self.assertEqual(org['invite_code'], "test_invite_code")

    def test_get_organization_id_by_task_id(self):
        c_name = "test_org"
        creater_id = self.dao.add_user("test_user", "test_password")
        c_id = self.dao.add_organization(c_name, "test_type", creater_id, "test_invite_code")
        task_id = self.dao.publish_task("task_name", creater_id, None, 0, 3600, c_id, "task_desc")
        self.assertEqual(c_id, self.dao.get_organization_id_by_task_id(task_id))

    def test_get_task_by_id(self):
        c_name = "test_org"
        creater_id = self.dao.add_user("test_user", "test_password")
        c_id = self.dao.add_organization(c_name, "test_type", creater_id, "test_invite_code")
        task_id = self.dao.publish_task("task_name", creater_id, None, 0, 3600, c_id, "task_desc")
        task = self.dao.get_task_by_id(task_id)
        print(task)
        self.assertIsNotNone(task)
        self.assertEqual(task['task_name'], "task_name")
        self.assertEqual(task['publisher_id'], creater_id)
        self.assertEqual(task['receiver_id'], None)
        self.assertEqual(task['task_state'], 0)
        self.assertEqual(task['c_id'], c_id)
        self.assertEqual(task['task_desc'], "task_desc")

    def test_delete_task(self):
        c_name = "test_org"
        creater_id = self.dao.add_user("test_user", "test_password")
        c_id = self.dao.add_organization(c_name, "test_type", creater_id, "test_invite_code")
        task_id = self.dao.publish_task("task_name", creater_id, None, 0, 3600, c_id, "task_desc")
        rows_affected = self.dao.delete_task(task_id)
        self.assertEqual(rows_affected, 1)        

    def test_get_user_info(self):
        u_id = self.dao.add_user("test_user", "test_password")   
        user_info = self.dao.get_user_base_info(u_id)
        self.assertIsNotNone(user_info)
        self.assertEqual(user_info['u_id'], u_id)
        self.assertEqual(user_info['username'], "test_user")
        
        user_all_info = self.dao.get_user_all_info(u_id)
        self.assertIsNotNone(user_all_info)
        self.assertEqual(user_all_info['u_id'], u_id)
        self.assertEqual(user_all_info['username'], "test_user")
        self.assertIsNotNone(user_all_info['register_time'])

    def test_get_user_info_by_name(self):
        u_id = self.dao.add_user("test_user", "test_password")
        user_info = self.dao.get_user_info_by_name("test_user")
        self.assertIsNotNone(user_info)
    
    def test_get_user_organizations(self):
        u_id = self.dao.add_user("test_user", "test_password")
        org_list = self.dao.get_user_organizations(u_id)
        self.assertEqual(len(org_list), 0)
        
        org_id1 = self.dao.add_organization("c_name_1", "family", u_id, 'code')
        org_id2 = self.dao.add_organization("c_name_2", "family", u_id, 'code')
        self.dao.add_user_to_organization(u_id, org_id1)
        org_list = self.dao.get_user_organizations(u_id) 
        self.assertEqual(len(org_list), 1)
        
        self.dao.add_user_to_organization(u_id, org_id2)
        org_list = self.dao.get_user_organizations(u_id)
        self.assertEqual(len(org_list), 2)
        self.assertEqual(org_list[0]['c_id'], org_id1)
        self.assertEqual(org_list[0]['c_name'], 'c_name_1')
        self.assertEqual(org_list[0]['c_type'], 'family')
        self.assertEqual(org_list[0]['invite_code'], 'code')
        self.assertEqual(org_list[1]['c_id'], org_id2)
        self.assertEqual(org_list[1]['c_name'], 'c_name_2')
        self.assertEqual(org_list[1]['c_type'], 'family')
        self.assertEqual(org_list[1]['invite_code'], 'code')

    def test_get_tasks_by_organization(self):
        # 创建用户
        u_id = self.dao.add_user("test_user", "test_password")
        # 创建组织
        org_id1 = self.dao.add_organization("c_name_1", "family", u_id, 'code')
        # 加入组织
        self.dao.add_user_to_organization(u_id, org_id1)
        # 发布任务1
        task_id = self.dao.publish_task("task_name_1", u_id, None, 0, 3600, org_id1, "task_desc")
        task_list = self.dao.get_tasks_by_organization(org_id1)
        self.assertEqual(len(task_list), 1)
        # 发布任务2
        task_id = self.dao.publish_task("task_name_2", u_id, None, 0, 3600, org_id1, "task_desc")
        task_list = self.dao.get_tasks_by_organization(org_id1)
        self.assertEqual(len(task_list), 2)

        task_list = self.dao.get_tasks_by_organization(0)
        self.assertEqual(len(task_list), 0)

    def test_get_tasks_by_user(self):
        # 创建用户
        u_id = self.dao.add_user("test_user", "test_password")
        # 创建组织
        org_id1 = self.dao.add_organization("c_name_1", "family", u_id, 'code')
        # 加入组织
        self.dao.add_user_to_organization(u_id, org_id1)
        # 发布任务1
        task_id = self.dao.publish_task("task_name_1", u_id, None, 0, 3600, org_id1, "task_desc")
        task_list = self.dao.get_tasks_by_user(u_id)
        self.assertEqual(len(task_list), 1)
        # 发布任务2
        task_id = self.dao.publish_task("task_name_2", u_id, None, 0, 3600, org_id1, "task_desc")
        task_list = self.dao.get_tasks_by_user(u_id)
        self.assertEqual(len(task_list), 2)

        task_list = self.dao.get_tasks_by_user(0)
        self.assertEqual(len(task_list), 0)
   
if __name__ == '__main__':
    unittest.main()
   
