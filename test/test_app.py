import subprocess
import time
import unittest
import sys
import os
import requests

# Add the parent directory of 'src' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..\src')))

# Now you can import from 'src'
from db_init import initialize_database
from ultils import *

class TestApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_url = "http://127.0.0.1:5000"

    @classmethod
    def tearDownClass(cls):
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
            response = requests.put(f'{self.base_url}/users/1/username', json=update_data)
            self.assertEqual(response.status_code, 401)

            # 登录
            response = requests.post(f'{self.base_url}/users/login', json=user_data)
            self.assertEqual(response.status_code, 200)
            update_id = response.json().get('user_id')
            headers = {
                "Authorization": f"Bearer {response.json()['access_token']}"
            }

            # 更新别人的账号
            update_id = update_id + 1
            response = requests.put(f'{self.base_url}/users/{update_id}/username', json=update_data, headers=headers)
            self.assertEqual(response.status_code, 403)

            # 更新自己账号
            update_id = update_id - 1
            response = requests.put(f'{self.base_url}/users/{update_id}/username', json=update_data, headers=headers)
            self.assertEqual(response.status_code, 200)

    def test_update_password(self):
            # 准备测试数据
            user_data = generate_user_data()

            # 发送POST请求创建用户
            response = requests.post(f'{self.base_url}/users/create', json=user_data)
            # 无登录更新
            response = requests.put(f'{self.base_url}/users/1/password', json=user_data)
            self.assertEqual(response.status_code, 401)
            # 登录
            response = requests.post(f'{self.base_url}/users/login', json=user_data)
            self.assertEqual(response.status_code, 200)
            headers = {
                "Authorization": f"Bearer {response.json()['access_token']}"
            }
            update_id = response.json()['user_id']

            # 更新别人的账号
            update_id = update_id + 1
            response = requests.put(f'{self.base_url}/users/{update_id}/password', headers=headers, json=user_data)
            self.assertEqual(response.status_code, 403)

            # 更新自己账号
            update_id = update_id - 1
            user_data['password'] = 'new_password'
            response = requests.put(f'{self.base_url}/users/{update_id}/password', headers=headers, json=user_data)
            self.assertEqual(response.status_code, 200)
            

    def test_delete_user(self):
            # 准备测试数据
            user_data = generate_user_data()

            # 发送POST请求创建用户
            response = requests.post(f'{self.base_url}/users/create', json=user_data)
            # 断言响应状态码为201（Created）
            self.assertEqual(response.status_code, 201)

            # 无登录删除
            response = requests.delete(f'{self.base_url}/users/1/delete')
            self.assertEqual(response.status_code, 401)

            # 登录后删除他人账号
            response = requests.post(f'{self.base_url}/users/login', json=user_data)
            self.assertEqual(response.status_code, 200)
            headers = {
                "Authorization": f"Bearer {response.json()['access_token']}"
            }
            delete_id = response.json()['user_id'] + 1
            response = requests.delete(f'{self.base_url}/users/{delete_id}/delete', headers=headers)
            self.assertEqual(response.status_code, 403)

            # 登录后删除自己账号
            delete_id = delete_id - 1
            response = requests.delete(f'{self.base_url}/users/{delete_id}/delete', headers=headers)
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
            org_id = response.json().get('c_id')
            # 获取组织
            response = requests.get(f'{self.base_url}/users/organizations', json=organization_data, headers=headers)
            self.assertEqual(response.status_code, 200)
            org_list = response.json().get('org_list')
            org_id_list = [org.get('c_id') for org in org_list]
            self.assertIn(org_id, org_id_list)
            

    def test_delete_organization(self):
            # 准备测试数据
            user_data = generate_user_data()
            organization_data = generate_org_data()
            # 发送POST请求创建用户
            response = requests.post(f'{self.base_url}/users/create', json=user_data)
            # 无登录删除
            response = requests.delete(f'{self.base_url}/organizations/1/delete')
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
            response = requests.delete(f'{self.base_url}/organizations/1/delete', headers=headers)
            self.assertEqual(response.status_code, 403)

            # 删除自己组织
            response = requests.delete(f'{self.base_url}/organizations/{org_id}/delete', headers=headers)
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
                'c_id': org_id,
                'c_name': '',
                'c_type': '',
                'invite_code': invite_code
            }
            response = requests.put(f'{self.base_url}/organizations/{org_id}/join', json=join_info)
            print(response)
            self.assertEqual(response.status_code, 401)

            # 加入组织
            response = requests.post(f'{self.base_url}/users/login', json=joiner_data)
            self.assertEqual(response.status_code, 200)
            headers = {
                "Authorization": f"Bearer {response.json()['access_token']}"
            }
            # 无邀请码加入
            join_info['c_id'] = org_id
            join_info['invite_code'] = ''
            response = requests.put(f'{self.base_url}/organizations/{org_id}/join', json=join_info, headers=headers)
            self.assertEqual(response.status_code, 400)
            # 加入不存在的组织
            join_info['c_id'] = 99999999
            join_info['invite_code'] = invite_code
            response = requests.put(f'{self.base_url}/organizations/{99999999}/join', json=join_info, headers=headers)
            self.assertEqual(response.status_code, 404)
            # 加入错误的邀请码
            join_info['c_id'] = org_id
            join_info['invite_code'] = '123456'
            response = requests.put(f'{self.base_url}/organizations/{org_id}/join', json=join_info, headers=headers)
            self.assertEqual(response.status_code, 403)
            # 加入组织
            join_info['c_id'] = org_id
            join_info['invite_code'] = invite_code
            response = requests.put(f'{self.base_url}/organizations/{org_id}/join', json=join_info, headers=headers)
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
                'c_id': org_id,
                'c_name': '',
                'c_type': '',
                'invite_code': invite_code
            }
            # 加入组织
            response = requests.post(f'{self.base_url}/users/login', json=joiner_data)
            self.assertEqual(response.status_code, 200)
            headers = {
                "Authorization": f"Bearer {response.json()['access_token']}"
            }
            response = requests.put(f'{self.base_url}/organizations/{org_id}/join', json=join_info, headers=headers)
            self.assertEqual(response.status_code, 200)

            # 无登录退出
            response = requests.put(f'{self.base_url}/organizations/{org_id}/leave')
            self.assertEqual(response.status_code, 401)

            # 退出组织成功
            response = requests.put(f'{self.base_url}/organizations/{org_id}/leave', headers=headers)
            self.assertEqual(response.status_code, 200)

    def test_publish_task(self):
            # 准备测试数据
            creator_data = generate_user_data()
            joiner_data = generate_user_data()
            organization_data = generate_org_data()
            task_data = generate_task_data()
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
                'c_id': org_id,
                'c_name': '',
                'c_type': '',
                'invite_code': invite_code
            }
            # 加入组织
            response = requests.post(f'{self.base_url}/users/login', json=joiner_data)
            self.assertEqual(response.status_code, 200)
            headers = {
                "Authorization": f"Bearer {response.json()['access_token']}"
            }
            response = requests.put(f'{self.base_url}/organizations/{org_id}/join', json=join_info, headers=headers)
            self.assertEqual(response.status_code, 200)

            # 创建者发布任务
            response = requests.post(f'{self.base_url}/users/login', json=creator_data)
            self.assertEqual(response.status_code, 200)
            headers = {
                "Authorization": f"Bearer {response.json()['access_token']}"
            }
            task_data['c_id'] = org_id
            task_data['publisher_id'] = response.json()['user_id']
            response = requests.put(f'{self.base_url}/tasks/publish', json=task_data, headers=headers)
            self.assertEqual(response.status_code, 200)

            # 加入者发布任务
            response = requests.post(f'{self.base_url}/users/login', json=joiner_data)
            self.assertEqual(response.status_code, 200)
            headers = {
                "Authorization": f"Bearer {response.json()['access_token']}"
            }
            task_data['c_id'] = org_id
            task_data['publisher_id'] = response.json()['user_id']
            response = requests.put(f'{self.base_url}/tasks/publish', json=task_data, headers=headers)
            self.assertEqual(response.status_code, 200)

    def test_accept_abandon_task(self):
        # 准备测试数据
        creator_data = generate_user_data()
        joiner_data = generate_user_data()
        organization_data = generate_org_data()
        task_data = generate_task_data()
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
            'c_id': org_id,
            'c_name': '', 
            'c_type': '',
            'invite_code': invite_code
        }
        # 加入组织
        response = requests.post(f'{self.base_url}/users/login', json=joiner_data)
        self.assertEqual(response.status_code, 200)
        headers = {
            "Authorization": f"Bearer {response.json()['access_token']}"
        }
        response = requests.put(f'{self.base_url}/organizations/{org_id}/join', json=join_info, headers=headers)
        self.assertEqual(response.status_code, 200)

        # 创建者发布任务
        response = requests.post(f'{self.base_url}/users/login', json=creator_data)
        self.assertEqual(response.status_code, 200)
        headers = {
            "Authorization": f"Bearer {response.json()['access_token']}" 
        }
        task_data['c_id'] = org_id
        task_data['publisher_id'] = response.json()['user_id']
        response = requests.put(f'{self.base_url}/tasks/publish', json=task_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        task_id = response.json()["task_id"]

        # 加入者接受任务
        response = requests.post(f'{self.base_url}/users/login', json=joiner_data)
        self.assertEqual(response.status_code, 200)
        headers = {
            "Authorization": f"Bearer {response.json()['access_token']}"
        }
        response = requests.put(f'{self.base_url}/tasks/{task_id}/accept', headers=headers)
        self.assertEqual(response.status_code, 200)
        # 重复接受任务
        response = requests.put(f'{self.base_url}/tasks/{task_id}/accept', headers=headers)
        self.assertEqual(response.status_code, 400)
        
        # 放弃任务
        response = requests.put(f'{self.base_url}/tasks/{task_id}/abandon', headers=headers)
        self.assertEqual(response.status_code, 200)
        
        # 重复放弃任务
        response = requests.put(f'{self.base_url}/tasks/{task_id}/abandon', headers=headers)
        self.assertEqual(response.status_code, 400)
        
        # 接受放弃的任务
        response = requests.put(f'{self.base_url}/tasks/{task_id}/accept', headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_accept_submit_confirm_task(self):
        # 准备测试数据
        creator_data = generate_user_data()
        joiner_data = generate_user_data()
        organization_data = generate_org_data()
        task_data = generate_task_data()
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
            'c_id': org_id,
            'c_name': '', 
            'c_type': '',
            'invite_code': invite_code
        }
        # 加入组织
        response = requests.post(f'{self.base_url}/users/login', json=joiner_data)
        self.assertEqual(response.status_code, 200)
        headers = {
            "Authorization": f"Bearer {response.json()['access_token']}"
        }
        response = requests.put(f'{self.base_url}/organizations/{org_id}/join', json=join_info, headers=headers)
        self.assertEqual(response.status_code, 200)

        # 创建者发布任务
        response = requests.post(f'{self.base_url}/users/login', json=creator_data)
        self.assertEqual(response.status_code, 200)
        headers = {
            "Authorization": f"Bearer {response.json()['access_token']}" 
        }
        task_data['c_id'] = org_id
        task_data['publisher_id'] = response.json()['user_id']
        response = requests.put(f'{self.base_url}/tasks/publish', json=task_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        task_id = response.json()["task_id"]

        # 加入者接受任务
        response = requests.post(f'{self.base_url}/users/login', json=joiner_data)
        self.assertEqual(response.status_code, 200)
        headers = {
            "Authorization": f"Bearer {response.json()['access_token']}"
        }
        response = requests.put(f'{self.base_url}/tasks/{task_id}/accept', headers=headers)
        self.assertEqual(response.status_code, 200)
        
        # 提交任务
        response = requests.put(f'{self.base_url}/tasks/{task_id}/submit', headers=headers)
        self.assertEqual(response.status_code, 200)
        
        # 重复提交任务
        response = requests.put(f'{self.base_url}/tasks/{task_id}/submit', headers=headers)
        self.assertEqual(response.status_code, 400)

        # 发布者登录
        response = requests.post(f'{self.base_url}/users/login', json=creator_data)
        self.assertEqual(response.status_code, 200)
        headers = {
            "Authorization": f"Bearer {response.json()['access_token']}"
        }
        # 确认任务
        response = requests.put(f'{self.base_url}/tasks/{task_id}/confirm', headers=headers)
        self.assertEqual(response.status_code, 200)
        
        # 重复确认任务
        response = requests.put(f'{self.base_url}/tasks/{task_id}/confirm', headers=headers)
        self.assertEqual(response.status_code, 400)
        
    def test_delete_task(self):
        # 准备测试数据
        creator_data = generate_user_data()
        organization_data = generate_org_data()
        task_data = generate_task_data()
        # 发送POST请求创建用户
        response = requests.post(f'{self.base_url}/users/create', json=creator_data)
        # 登录
        response = requests.post(f'{self.base_url}/users/login', json=creator_data)
        self.assertEqual(response.status_code, 200)
        headers = {
            "Authorization": f"Bearer {response.json()['access_token']}"
        }
        u_id = response.json()['user_id']
        # 创建组织
        response = requests.post(f'{self.base_url}/organizations/create', json=organization_data, headers=headers)
        self.assertEqual(response.status_code, 201)
        org_id = response.json()['c_id']
        
        # 发布任务
        task_data = generate_task_data()
        task_data['c_id'] = org_id
        task_data['publisher_id'] = u_id
        response = requests.put(f'{self.base_url}/tasks/publish', json=task_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        task_id = response.json()["task_id"]

        # 未认证删除任务
        response = requests.delete(f'{self.base_url}/tasks/{task_id}/delete')
        self.assertEqual(response.status_code, 401)
        
        # 创建新用户
        new_user_data = generate_user_data()
        response = requests.post(f'{self.base_url}/users/create', json=new_user_data)
        self.assertEqual(response.status_code, 201)     
        # 新用户登录
        response = requests.post(f'{self.base_url}/users/login', json=new_user_data)
        self.assertEqual(response.status_code, 200)   
        new_user_headers = {
            "Authorization": f"Bearer {response.json()['access_token']}" 
        }
        # 新用户删除任务
        response = requests.delete(f'{self.base_url}/tasks/{task_id}/delete', headers=new_user_headers)
        self.assertEqual(response.status_code, 403)

        # 删除任务
        response = requests.delete(f'{self.base_url}/tasks/{task_id}/delete', headers=headers)
        self.assertEqual(response.status_code, 200)

        # 重复删除任务
        response = requests.delete(f'{self.base_url}/tasks/{task_id}/delete', headers=headers)
        self.assertEqual(response.status_code, 404)
        
    def test_get_user_info(self):
        # 准备测试数据
        user_a = generate_user_data()
        user_b = generate_user_data()
        # 发送POST请求创建用户
        response = requests.post(f'{self.base_url}/users/create', json=user_a)
        print('---ccc---', response.json())
        u_id_a = response.json().get('user_id')
        response = requests.post(f'{self.base_url}/users/create', json=user_b)
        u_id_b = response.json().get('user_id')
        # 登录用户a
        response = requests.post(f'{self.base_url}/users/login', json=user_a)
        self.assertEqual(response.status_code, 200)
        headers = {
            "Authorization": f"Bearer {response.json()['access_token']}" 
        }
        # 获取用户a信息
        response = requests.get(f'{self.base_url}/users/{u_id_a}/info', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json().get('user_info').get('u_id'))
        self.assertIsNotNone(response.json().get('user_info').get('username'))
        self.assertIsNone(response.json().get('user_info').get('password'))
        self.assertIsNotNone(response.json().get('user_info').get('register_time'))
        # 获取用户b信息
        response = requests.get(f'{self.base_url}/users/{u_id_b}/info', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json().get('user_info').get('u_id'))
        self.assertIsNotNone(response.json().get('user_info').get('username'))
        self.assertIsNone(response.json().get('user_info').get('password'))
        self.assertIsNone(response.json().get('user_info').get('register_time'))
      
    def test_get_user_info_by_name(self):
        # 准备测试数据
        user_a = generate_user_data()

        # 发送POST请求创建用户
        response = requests.post(f'{self.base_url}/users/create', json=user_a)
        self.assertEqual(response.status_code, 201)
        u_id_a = response.json().get('user_id')
        # 登录用户a
        response = requests.post(f'{self.base_url}/users/login', json=user_a)
        self.assertEqual(response.status_code, 200)
        headers = {
            "Authorization": f"Bearer {response.json()['access_token']}"
        }
        # 获取用户a信息
        response = requests.get(f'{self.base_url}/users/{user_a["username"]}/info', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json().get('user_info').get('u_id'))
        self.assertIsNotNone(response.json().get('user_info').get('username'))
        self.assertIsNone(response.json().get('user_info').get('password'))
        self.assertIsNone(response.json().get('user_info').get('register_time'))

    def test_get_organization_info(self):
        # 准备测试数据
        user_a = generate_user_data()
        org_a = generate_org_data()
        # 发送POST请求创建用户
        response = requests.post(f'{self.base_url}/users/create', json=user_a)
        self.assertEqual(response.status_code, 201)
        u_id_a = response.json().get('user_id')
        # 登录用户a
        response = requests.post(f'{self.base_url}/users/login', json=user_a)
        self.assertEqual(response.status_code, 200)
        headers = {
            "Authorization": f"Bearer {response.json()['access_token']}"
        }
        # 创建组织
        response = requests.post(f'{self.base_url}/organizations/create', json=org_a, headers=headers)
        self.assertEqual(response.status_code, 201)
        org_id = response.json().get('c_id')
        print(response.json())
        
        # Get组织信息
        response = requests.get(f'{self.base_url}/organizations/{org_id}/info', json=org_a, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json().get('org_info').get('c_id'))
        self.assertIsNotNone(response.json().get('org_info').get('c_name'))
        self.assertIsNotNone(response.json().get('org_info').get('c_type'))
        self.assertIsNotNone(response.json().get('org_info').get('creator_id'))
        self.assertIsNotNone(response.json().get('org_info').get('invite_code'))
        self.assertIsNotNone(response.json().get('org_info').get('create_time'))

    def test_get_user_organizations(self):
        # 准备测试数据
        user_a = generate_user_data()
        org_a = generate_org_data()
        org_b = generate_org_data()
        # 发送POST请求创建用户
        response = requests.post(f'{self.base_url}/users/create', json=user_a)
        self.assertEqual(response.status_code, 201)
        u_id_a = response.json().get('user_id')
        # 登录用户a
        response = requests.post(f'{self.base_url}/users/login', json=user_a)
        self.assertEqual(response.status_code, 200)
        headers = {
            "Authorization": f"Bearer {response.json()['access_token']}"
        }
        
        response = requests.get(f'{self.base_url}/users/organizations', headers=headers)
        self.assertEqual(response.status_code, 404)
        org_list = response.json().get('org_list')
        self.assertIsNone(org_list)
        
        # 创建组织a
        response = requests.post(f'{self.base_url}/organizations/create', json=org_a, headers=headers)
        self.assertEqual(response.status_code, 201)

        # 查询user_a的组织
        response = requests.get(f'{self.base_url}/users/organizations', headers=headers)
        self.assertEqual(response.status_code, 200)
        org_list = response.json().get('org_list')
        self.assertEqual(len(org_list), 1)

        # 创建组织b
        response = requests.post(f'{self.base_url}/organizations/create', json=org_b, headers=headers)
        self.assertEqual(response.status_code, 201)
        
        # 再次查询user_a的组织
        response = requests.get(f'{self.base_url}/users/organizations', headers=headers)
        self.assertEqual(response.status_code, 200)
        org_list = response.json().get('org_list')
        self.assertEqual(len(org_list), 2)

    def test_get_organization_tasks(self):
         # 准备测试数据
        user_a = generate_user_data()
        org_a = generate_org_data()
        # 发送POST请求创建用户
        response = requests.post(f'{self.base_url}/users/create', json=user_a)
        self.assertEqual(response.status_code, 201)
        u_id_a = response.json().get('user_id')
        # 登录用户a
        response = requests.post(f'{self.base_url}/users/login', json=user_a)
        self.assertEqual(response.status_code, 200)
        headers = {
            "Authorization": f"Bearer {response.json()['access_token']}"
        }
        # 创建组织a
        response = requests.post(f'{self.base_url}/organizations/create', json=org_a, headers=headers)
        self.assertEqual(response.status_code, 201)
        org_id_a = response.json().get('c_id')
        # 发布任务
        task_data = generate_task_data()
        task_data['c_id'] = org_id_a
        task_data['publisher_id'] = u_id_a
        response = requests.put(f'{self.base_url}/tasks/publish', json=task_data, headers=headers)
        self.assertEqual(response.status_code, 200)

        # 查询成功
        response = requests.get(f'{self.base_url}/organizations/{org_id_a}/tasks', headers=headers)
        self.assertEqual(response.status_code, 200)
        task_list = response.json().get('tasks')
        self.assertEqual(len(task_list), 1)

        # 非法查询，未认证
        response = requests.get(f'{self.base_url}/organizations/{org_id_a}/tasks')
        self.assertEqual(response.status_code, 401)

        # 非法查询，无权限访问组织
        response = requests.get(f'{self.base_url}/organizations/{0}/tasks', headers=headers)
        self.assertEqual(response.status_code, 403)

    def test_get_user_tasks(self):
         # 准备测试数据
        user_a = generate_user_data()
        org_a = generate_org_data()
        # 发送POST请求创建用户
        response = requests.post(f'{self.base_url}/users/create', json=user_a)
        self.assertEqual(response.status_code, 201)
        u_id_a = response.json().get('user_id')
        # 登录用户a
        response = requests.post(f'{self.base_url}/users/login', json=user_a)
        self.assertEqual(response.status_code, 200)
        headers = {
            "Authorization": f"Bearer {response.json()['access_token']}"
        }
        # 创建组织a
        response = requests.post(f'{self.base_url}/organizations/create', json=org_a, headers=headers)
        self.assertEqual(response.status_code, 201)
        org_id_a = response.json().get('c_id')
        # 发布任务
        task_data = generate_task_data()
        task_data['c_id'] = org_id_a
        task_data['publisher_id'] = u_id_a
        response = requests.put(f'{self.base_url}/tasks/publish', json=task_data, headers=headers)
        self.assertEqual(response.status_code, 200)

        # 查询成功
        response = requests.get(f'{self.base_url}/users/tasks', headers=headers)
        self.assertEqual(response.status_code, 200)
        task_list = response.json().get('tasks')
        self.assertEqual(len(task_list), 1)

        # 非法查询，未认证
        response = requests.get(f'{self.base_url}/users/tasks')
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()