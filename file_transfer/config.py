import os,sys,json
from PIL import Image

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def find_cert_and_key():
    running_directory = os.path.dirname(sys.executable) if hasattr(sys, 'executable') else os.path.abspath('.')
    
    cert1 = None
    key1 = None
    
    for file_name in os.listdir(running_directory):
        file_path = os.path.join(running_directory, file_name)
        
        if file_name.endswith('.crt'):
            cert1 = file_path
        elif file_name.endswith('.key'):
            key1 = file_path
    
    return cert1, key1

class ConfigManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            print(f"配置文件存在，将加载配置文件")
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            print("配置文件不存在，将使用默认配置")
            return {
                "shared_folder": os.getcwd(),
                "target_folder": os.path.join(os.getcwd(), "uploads")
            }

    def save_config(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
        print("配置文件已保存")

    def update_shared_folder(self, shared_folder):
        self.config["shared_folder"] = shared_folder
        self.save_config()
        print(f"共享文件夹路径已更新{shared_folder}")

    def update_target_folder(self, target_folder):
        self.config["target_folder"] = target_folder
        self.save_config()
        print(f"上传文件夹路径已更新{target_folder}")

    def get_shared_folder(self):
        return self.config.get("shared_folder", os.getcwd())

    def get_target_folder(self):
        return self.config.get("target_folder", os.path.join(os.getcwd(), "uploads"))

image_path = os.path.join("icon", "icon.jpg")
image = Image.open(get_resource_path(image_path))

config_path = os.path.join("icon", "config.json")
CONFIG_PATH = get_resource_path(config_path)


'''
CONFIG_PATH = "D:/VSCode/environmental/project/FFTUSR/file_transfer/icon/config.json"
image=Image.open("D:/VSCode/environmental/project/FFTUSR/file_transfer/icon/icon.jpg")
'''
cert_file,key_file = find_cert_and_key()

print("证书文件路径：",cert_file)
print("密钥文件路径：",key_file)

config_manager = ConfigManager(CONFIG_PATH)
DEFAULT_SHARED_FOLDER = os.path.abspath(config_manager.config.get("shared_folder", os.getcwd()))
DEFAULT_TARGET_FOLDER = os.path.abspath(config_manager.config.get("target_folder", os.path.join(os.getcwd(), "uploads")))
SHARED_FOLDER = DEFAULT_SHARED_FOLDER
TARGET_FOLDER = DEFAULT_TARGET_FOLDER
PORT = 12345
UPLOAD_PROGRESS = {}
