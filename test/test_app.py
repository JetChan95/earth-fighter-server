import subprocess
import time
import unittest
import mysql.connector
import json
import sys
import os
import requests
from unittest.mock import patch

# Add the parent directory of 'src' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..\src')))

# Now you can import from 'src'
import app
from db_init import initialize_database
from ultils import generate_org_data, generate_user_data

class TestApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 初始化数据库
        # initialize_database()
        # 启动Flask应用
        # cls.process = subprocess.Popen(['python', 'src/app.py'])
        # time.sleep(1)  # 等待应用启动
        cls.base_url = "http://127.0.0.1:5000"

    @classmethod
    def tearDownClass(cls):
       # 关闭Flask应用
        # cls.process.terminate()
        # cls.process.wait()
        pass
        
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_user(self):
            # 准备测试数据
            user_data = generate_user_data()

            # 发送POST请求创建用户
            response = requests.post(f'{self.base_url}/users/create', json=user_data)
            # 断言响应状态码为201（Created）
            self.assertEqual(response.status_code, 201)

            # 重复创建用户
            response = requests.post(f'{self.base_url}/users/create', json=user_data)
            # 断言响应状态码为400（Bad Request）
            self.assertEqual(response.status_code, 400)

    def test_login(self):
            # 准备测试数据
            user_data = generate_user_data()

            # 发送POST请求创建用户
            response = requests.post(f'{self.base_url}/users/create', json=user_data)
            # 登录
            response = requests.post(f'{self.base_url}/users/login', json=user_data)
            # 断言响应状态码为200（OK）
            self.assertEqual(response.status_code, 200)
    def test_update_user(self):
            # 准备测试数据
            user_data = generate_user_data()

            # 发送POST请求创建用户
            response = requests.post(f'{self.base_url}/users/create', json=user_data)

            # 准备更新数据
            update_data = generate_user_data()
            # 无登录更新
            response = requests.put(f'{self.base_url}/users/update/1', json=update_data)
            self.assertEqual(response.status_code, 401)

            # 登录
            response = requests.post(f'{self.base_url}/users/login', json=user_data)
            self.assertEqual(response.status_code, 200)
            delete_id = response.json().get('data')['user_id']
            headers = {
                "Authorization": f"Bearer {response.json()['access_token']}"
            }

            # 更新别人的账号
            delete_id = delete_id + 1
            response = requests.put(f'{self.base_url}/users/update/{delete_id}', json=update_data, headers=headers)
            self.assertEqual(response.status_code, 403)

            # 更新自己账号
            delete_id = delete_id - 1
            response = requests.put(f'{self.base_url}/users/update/{delete_id}', json=update_data, headers=headers)
            self.assertEqual(response.status_code, 200)


    def test_delete_user(self):
            # 准备测试数据
            user_data = generate_user_data()

            # 发送POST请求创建用户
            response = requests.post(f'{self.base_url}/users/create', json=user_data)
            # 断言响应状态码为201（Created）
            self.assertEqual(response.status_code, 201)

            # 无登录删除
            response = requests.delete(f'{self.base_url}/users/delete/1')
            self.assertEqual(response.status_code, 401)

            # 登录后删除他人账号
            response = requests.post(f'{self.base_url}/users/login', json=user_data)
            self.assertEqual(response.status_code, 200)
            headers = {
                "Authorization": f"Bearer {response.json()['access_token']}"
            }
            delete_id = response.json()['data']['user_id'] + 1
            response = requests.delete(f'{self.base_url}/users/delete/{delete_id}', headers=headers)
            self.assertEqual(response.status_code, 403)

            # 登录后删除自己账号
            delete_id = delete_id - 1
            response = requests.delete(f'{self.base_url}/users/delete/{delete_id}', headers=headers)
            self.assertEqual(response.status_code, 200)

    def test_create_organization(self):
            # 准备测试数据
            user_data = generate_user_data()
            organization_data = generate_org_data()
            # 发送POST请求创建用户
            response = requests.post(f'{self.base_url}/users/create', json=user_data)
            # 无登录创建
            response = requests.post(f'{self.base_url}/organizations/create', json=organization_data)
            self.assertEqual(response.status_code, 401)

            # 登录
            response = requests.post(f'{self.base_url}/users/login', json=user_data)
            self.assertEqual(response.status_code, 200)
            headers = {
                "Authorization": f"Bearer {response.json()['access_token']}"
            }

            # 创建组织
            response = requests.post(f'{self.base_url}/organizations/create', json=organization_data, headers=headers)
            self.assertEqual(response.status_code, 201)

    def test_delete_organization(self):
            # 准备测试数据
            user_data = generate_user_data()
            organization_data = generate_org_data()
            # 发送POST请求创建用户
            response = requests.post(f'{self.base_url}/users/create', json=user_data)
            # 无登录删除
            response = requests.delete(f'{self.base_url}/organizations/delete/1')
            self.assertEqual(response.status_code, 401)

            # 登录
            response = requests.post(f'{self.base_url}/users/login', json=user_data)
            self.assertEqual(response.status_code, 200)
            headers = {
                "Authorization": f"Bearer {response.json()['access_token']}"
            }
            # 创建组织
            response = requests.post(f'{self.base_url}/organizations/create', json=organization_data, headers=headers)
            self.assertEqual(response.status_code, 201)
            
            print(response.json())
            org_id = response.json()['c_id']
            # 删除他人组织
            response = requests.delete(f'{self.base_url}/organizations/delete/1', headers=headers)
            self.assertEqual(response.status_code, 403)

            # 删除自己组织
            response = requests.delete(f'{self.base_url}/organizations/delete/{org_id}', headers=headers)
            self.assertEqual(response.status_code, 200)

    def test_join_organization(self):
            # 准备测试数据
            creator_data = generate_user_data()
            joiner_data = generate_user_data()
            organization_data = generate_org_data()            
            # 发送POST请求创建用户
            response = requests.post(f'{self.base_url}/users/create', json=creator_data)
            response = requests.post(f'{self.base_url}/users/create', json=joiner_data)
            #创建组织
            response = requests.post(f'{self.base_url}/users/login', json=creator_data)
            self.assertEqual(response.status_code, 200)
            headers = {
                "Authorization": f"Bearer {response.json()['access_token']}"
            }
            response = requests.post(f'{self.base_url}/organizations/create', json=organization_data, headers=headers)
            self.assertEqual(response.status_code, 201)
            org_id = response.json()['c_id']
            invite_code = response.json()['invite_code']

            # 无登录加入
            join_info = {
                'org_id': org_id, 
                'invite_code': invite_code
            }
            response = requests.post(f'{self.base_url}/organizations/join', json=join_info)
            self.assertEqual(response.status_code, 401)

            # 加入组织
            response = requests.post(f'{self.base_url}/users/login', json=joiner_data)
            self.assertEqual(response.status_code, 200)
            headers = {
                "Authorization": f"Bearer {response.json()['access_token']}"
            }
            # 无组织ID加入
            join_info = {
                'invite_code': invite_code
            }
            response = requests.post(f'{self.base_url}/organizations/join', json=join_info, headers=headers)
            self.assertEqual(response.status_code, 400)
            # 无邀请码加入
            join_info = {
                'org_id': org_id
            }
            response = requests.post(f'{self.base_url}/organizations/join', json=join_info, headers=headers)
            self.assertEqual(response.status_code, 400)
            # 加入不存在的组织
            join_info = {
                'org_id': -1,
                'invite_code': invite_code
            }
            response = requests.post(f'{self.base_url}/organizations/join', json=join_info, headers=headers)
            self.assertEqual(response.status_code, 404)
            # 加入错误的邀请码
            join_info = {
                'org_id': org_id,
                'invite_code': '000000'
            }
            response = requests.post(f'{self.base_url}/organizations/join', json=join_info, headers=headers)
            self.assertEqual(response.status_code, 403)
            # 加入组织
            join_info = {
                'org_id': org_id,
                'invite_code': invite_code
            }
            response = requests.post(f'{self.base_url}/organizations/join', json=join_info, headers=headers)
            self.assertEqual(response.status_code, 200)

    def test_leave_organization(self):
           # 准备测试数据
            creator_data = generate_user_data()
            joiner_data = generate_user_data()
            organization_data = generate_org_data()            
            # 发送POST请求创建用户
            response = requests.post(f'{self.base_url}/users/create', json=creator_data)
            response = requests.post(f'{self.base_url}/users/create', json=joiner_data)
            #创建组织
            response = requests.post(f'{self.base_url}/users/login', json=creator_data)
            self.assertEqual(response.status_code, 200)
            headers = {
                "Authorization": f"Bearer {response.json()['access_token']}"
            }
            response = requests.post(f'{self.base_url}/organizations/create', json=organization_data, headers=headers)
            self.assertEqual(response.status_code, 201)
            org_id = response.json()['c_id']
            invite_code = response.json()['invite_code']
            join_info = {
                'org_id': org_id, 
                'invite_code': invite_code
            }
            # 加入组织
            response = requests.post(f'{self.base_url}/users/login', json=joiner_data)
            self.assertEqual(response.status_code, 200)
            headers = {
                "Authorization": f"Bearer {response.json()['access_token']}"
            }
            response = requests.post(f'{self.base_url}/organizations/join', json=join_info, headers=headers)
            self.assertEqual(response.status_code, 200)

            # 无登录退出
            response = requests.delete(f'{self.base_url}/organizations/leave/{org_id}')
            self.assertEqual(response.status_code, 401)

            # 退出组织成功
            response = requests.delete(f'{self.base_url}/organizations/leave/{org_id}', headers=headers)
            self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()