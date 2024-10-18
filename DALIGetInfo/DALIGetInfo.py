
"""
The script calculates number of lights and switches for every
electrical circuit that found in electrical panel.
Optional can calculate and propose DALI ports.
"""
# ================ system imports
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
sys.path.append(IN[0].DirectoryName)  # type: ignore

import System
from System import Array
from System.Collections.Generic import *

# ================ Revit imports
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# ================ Python imports
import re
import importlib
import toolsrvt
# importlib.reload(toolsrvt)
import dali_sys
importlib.reload(dali_sys)
from dali_sys import DaliSys

# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
app = uiapp.Application

reload = IN[1]  # type: ignore
info_list = list()
boards_list = list()

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# for board in board_list:
board = UnwrapElement(IN[3])  # type: ignore
propose_DALI = IN[2]  # type: ignore

circuits_to_calculate = toolsrvt.elsys_by_brd(board)[1]
circuits_to_calculate = [circuit for circuit in circuits_to_calculate
	if circuit.CircuitType == Autodesk.Revit.DB.Electrical.CircuitType.Circuit]

if not circuits_to_calculate:
	raise ValueError("No circuits found")

dali_systems = [DaliSys(i) for i in circuits_to_calculate]

# calculate DALI controls automaticaly
if propose_DALI:
	DaliSys.get_DALI_controls_info(dali_systems)

for obj_sys in dali_systems:
	obj_sys.create_params_list()

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

DaliSys.write_info()

# # =========End transaction
TransactionManager.Instance.TransactionTaskDone()

# OUT = info_list
OUT = DaliSys.params_to_set
# OUT = [i.DALI_control for i in dali_systems]
