import unittest
import mysql.connector
import json
import sys
import os

# Add the parent directory of 'src' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
        self.cursor.execute("DELETE FROM tasks")
        self.cursor.execute("DELETE FROM users")
        self.cursor.execute("DELETE FROM organizations")
        self.db.commit()

    def test_add_user(self):
        u_id = self.dao.add_user("test_user", "test_password")
        self.cursor.execute("SELECT * FROM users WHERE u_id = %s", (u_id,))
        user = self.cursor.fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user[1], "test_user")
        self.assertEqual(user[2], "test_password")

    def test_delete_user(self):
        u_id = self.dao.add_user("test_user", "test_password")
        rows_affected = self.dao.delete_user(u_id)
        self.assertEqual(rows_affected, 1)
        self.cursor.execute("SELECT is_deleted FROM users WHERE u_id = %s", (u_id,))
        is_deleted = self.cursor.fetchone()[0]
        self.assertEqual(is_deleted, 1)


    def test_update_user(self):
        u_id = self.dao.add_user("test_user", "test_password")
        rows_affected = self.dao.update_user(u_id, "updated_user", "updated_password")
        self.assertEqual(rows_affected, 1)
        self.cursor.execute("SELECT * FROM users WHERE u_id = %s", (u_id,))
        user = self.cursor.fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user[1], "updated_user")
        self.assertEqual(user[2], "updated_password")

    def test_user_login(self):
        self.dao.add_user("test_user", "test_password")
        user = self.dao.user_login("test_user", "test_password")
        self.assertIsNotNone(user)
        self.assertEqual(user[1], "test_user")
        self.assertEqual(user[2], "test_password")

    def test_add_organization(self):
        c_id = self.dao.add_organization("test_org", "test_type")
        self.cursor.execute("SELECT * FROM organizations WHERE c_id = %s", (c_id,))
        org = self.cursor.fetchone()
        self.assertIsNotNone(org)
        self.assertEqual(org[1], "test_org")
        self.assertEqual(org[2], "test_type")

    def test_delete_organization(self):
        c_id = self.dao.add_organization("test_org", "test_type")
        rows_affected = self.dao.delete_organization(c_id)
        self.assertEqual(rows_affected, 1)
        self.cursor.execute("SELECT is_deleted FROM organizations WHERE c_id = %s", (c_id,))
        is_deleted = self.cursor.fetchone()[0]
        self.assertEqual(is_deleted, 1)


    def test_publish_task(self):
        publisher_id = self.dao.add_user("publisher", "publisher_password")
        receiver_id = self.dao.add_user("receiver", "receiver_password")
        task_id = self.dao.publish_task(publisher_id, receiver_id, 0, 3600)
        self.cursor.execute("SELECT * FROM tasks WHERE task_id = %s", (task_id,))
        task = self.cursor.fetchone()
        self.assertIsNotNone(task)
        self.assertEqual(task[1], publisher_id)
        self.assertEqual(task[2], receiver_id)
        self.assertEqual(task[3], 0)

    def test_update_task_status(self):
        publisher_id = self.dao.add_user("publisher", "publisher_password")
        receiver_id = self.dao.add_user("receiver", "receiver_password")
        task_id = self.dao.publish_task(publisher_id, receiver_id, 0, 3600)
        rows_affected = self.dao.update_task_status(task_id, 1)
        self.assertEqual(rows_affected, 1)        
        self.cursor.execute("SELECT * FROM tasks WHERE task_id = %s", (task_id,))
        task = self.cursor.fetchone()
        self.assertIsNotNone(task)
        self.assertEqual(task[3], 1)

if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestSuite()
    # suite.addTest(TestEarthFighterDAO('test_delete_user'))
    # unittest.TextTestRunner().run(suite)
   
