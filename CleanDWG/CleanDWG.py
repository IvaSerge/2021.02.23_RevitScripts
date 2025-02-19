import sys
dir_path = IN[0].DirectoryName  # type: ignore
sys.path.append(r"C:\Users\sivasiuk\AppData\Local\python-3.9.12-embed-amd64\Lib\site-packages")
sys.path.append(r"C:\Users\sivasiuk\AppData\Local\python-3.9.12-embed-amd64\Lib\site-packages\win32")
sys.path.append(r"C:\Users\sivasiuk\AppData\Local\python-3.9.12-embed-amd64\Lib\site-packages\win32\lib")
sys.path.append(dir_path)


# ================ Python imports
from importlib import reload

# ================ local imports
import toolsdwg
reload(toolsdwg)
from toolsdwg import *

# ================================
# =========== Main code ==========
# ================================

acad_instance = get_acad_instance()
if acad_instance:
	doc = get_active_document(acad_instance)
	print(f"Active document: {doc.Name}")

# unlock_layers(doc)
# on_layers(doc)
# selection = get_selection(doc)


OUT = get_visible_hatches(doc)
