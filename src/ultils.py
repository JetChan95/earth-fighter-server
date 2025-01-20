import random
import string
import config_manager

cfg = config_manager.ConfigManager()

def generate_user_data():
    username = ''.join(random.choices(string.ascii_letters, k=6))
    password = ''.join(random.choices(string.ascii_letters, k=6))
    return {'username': username, 'password': password}

def generate_org_data():
    org_config = cfg.get_organization_types()
    org_types = [item['type_name'] for item in org_config]
    org_name = ''.join(random.choices(string.ascii_letters, k=6))
    org_type = random.choice(org_types)
    return {'c_name': org_name, 'c_type': org_type}

def generate_invite_code():
    """
    生成随机的6位大小写字母组合的邀请码
    """
    return ''.join(random.choices(string.ascii_letters, k=6))