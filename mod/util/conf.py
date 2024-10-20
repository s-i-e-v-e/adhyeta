import os
import platform
USER_ROOT = os.environ['APPDATA'] if platform.system() == "Windows" else os.environ['XDG_DATA_HOME']
DATA_ROOT = f"{USER_ROOT}/adhyeta"
DB_FILE = f"{DATA_ROOT}/data.sqlite3"

os.makedirs(DATA_ROOT, exist_ok=True)