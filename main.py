# %%
import os
import dotenv; dotenv.load_dotenv()
from pyicloud import PyiCloudService
from pyicloud.services.drive import DriveNode, DriveService

api = PyiCloudService(os.environ.get('LOGIN'), os.environ.get('PASSWORD'))

def refresh_api():
    global api
    api = PyiCloudService(os.environ.get('LOGIN'), os.environ.get('PASSWORD'))

# %%
if api.requires_2fa:
    print("Two-factor authentication required.")
    code = input("Enter the code you received of one of your approved devices: ")
    result = api.validate_2fa_code(code)
    print("Code validation result: %s" % result)
else:
    print("2FA not needed")

# %%
def get_folder(path: list) -> DriveNode:
    refresh_api()
    node = api.drive
    for el in path:
        node = node[el]    
    
    assert node, f"Folder {path} not found"
    
    return node

def _add_folder(base: DriveNode, name: str):       
    try:
        base.mkdir(name)
    except Exception as e:
        print(f"Failed to create {name}: {e}")    

def _add_file(base: DriveNode, file: str):
    with open(file, 'rb') as f:
        try:
            base.upload(f)
        except Exception as e:
            print(f"Failed to upload {file}: {e}")


def add_folder(base: DriveNode, name: str, recursive_path: list = []) -> DriveNode:
    if not base.get(name):    
        _add_folder(base, name)
        base = get_folder(recursive_path)  
    return base.get(name)


def add_file(base: DriveNode, file: str, recursive_path: list = []):
    _add_file(base, file)
    base = get_folder(recursive_path)  
    # base[file].rename(os.path.basename(file))
    
def upload_folder(path: str, base: DriveNode, recursive_path: list = []):
    refresh_api()
    folder = add_folder(base, os.path.basename(path), recursive_path)
    
    # add files
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    files = [f for f in files if not folder.get(f)]
    for file in files:
        add_file(folder, os.path.join(path, file), recursive_path)        
    
    # add dirs
    dirs = (d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)))
    for dir in dirs:
        upload_folder(os.path.join(path, dir), folder, recursive_path + [dir])

# %%
personal = api.drive['Personal']
upload_folder(r'D:\Filip\test', personal, ['Personal'])



