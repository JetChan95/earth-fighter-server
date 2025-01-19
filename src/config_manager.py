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
        with open('config/app.json', 'r') as f:
            self._config = json.load(f)

    def get_config(self):
        return self._config
