import random
import string
import config_manager
from schemas import *
cfg = config_manager.ConfigManager()

def generate_user_data():
    username = ''.join(random.choices(string.ascii_letters, k=6))
    password = ''.join(random.choices(string.ascii_letters, k=6))
    user_data = {
        'user_id': 0,
        'username': username,
        'password': password,
        'register_time': ''
    }
    return user_data

def generate_login_data():
    username = ''.join(random.choices(string.ascii_letters, k=6))
    password = ''.join(random.choices(string.ascii_letters, k=6))
    user_data = {
        'username': username,
        'password': password,
    }
    return user_data

def generate_org_data():
    org_config = cfg.get_organization_types()
    org_types = [item['type_name'] for item in org_config]
    org_name = ''.join(random.choices(string.ascii_letters, k=6))
    org_type = random.choice(org_types)
    org_data = {
        'c_id': 0,
        'c_name': org_name,
        'c_type': org_type,
        'invite_code': ''
        }

    return org_data

def generate_invite_code():
    """
    生成随机的6位大小写字母组合的邀请码
    """
    return ''.join(random.choices(string.ascii_letters, k=6))