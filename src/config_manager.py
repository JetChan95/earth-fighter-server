import json

class ConfigManager:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        with open('config/app.json', 'r', encoding='utf-8') as f:
            self._config = json.load(f)

    def get_config(self):
        return self._config
    
    def get_organization_types(self):
        return self._config['organization_types']

    def get_user_roles(self):
        return self._config['user_roles']
    
    def get_task_status(self):
        return self._config['task_status']
    
    def is_org_type_valid(self, org_type):
        data = self.get_organization_types()
        return any(item["type_name"] == org_type for item in data)
