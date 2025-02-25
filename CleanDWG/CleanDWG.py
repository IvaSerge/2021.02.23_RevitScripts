import sys
dir_path = IN[0].DirectoryName  # type: ignore
sys.path.append(r"C:\Users\sivasiuk\AppData\Local\python-3.9.12-embed-amd64\Lib\site-packages")
sys.path.append(r"C:\Users\sivasiuk\AppData\Local\python-3.9.12-embed-amd64\Lib\site-packages\win32")
sys.path.append(r"C:\Users\sivasiuk\AppData\Local\python-3.9.12-embed-amd64\Lib\site-packages\win32\lib")
sys.path.append(dir_path)

import System
from System import Array
from System import Single
from System import Double

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

# on_layers(doc)
# selection = get_selection(doc)
# block_all_to_layer_null()
# attributes = burst_block(doc, selection[0]["obj"].Name)

# Steps to clean drawing
# 1. Purge DWG
# purge_total(doc)

# 2. Delete frozen layers
# unlock_layers(doc)

# 3. Burst
point_test = Array[float]([0.0, 0.0, 0.0])
point_test_end = Array[float]([0.0, 10.0, 0.0])
# mtext = doc.ModelSpace.AddText("Test", point_test, 10)
a_line = doc.ModelSpace.AddLine(1, 0)

# OUT = dir(doc.ModelSpace.AddText())
OUT = point_test