import yaml
import json
import os

def load_config(config_path):
    if not os.path.exists(config_path):
        return {}
    
    if config_path.endswith('.yaml') or config_path.endswith('.yml'):
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    elif config_path.endswith('.json'):
        with open(config_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        raise ValueError("Unsupported config file format")

def save_config(config, config_path):
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    if config_path.endswith('.yaml') or config_path.endswith('.yml'):
        with open(config_path, 'w', encoding='utf-8') as file:
            yaml.dump(config, file, allow_unicode=True)
    elif config_path.endswith('.json'):
        with open(config_path, 'w', encoding='utf-8') as file:
            json.dump(config, file, ensure_ascii=False, indent=2)
    else:
        raise ValueError("Unsupported config file format")
