

# "E_Light_number"
# "Switching Unit"
# "Control Unit"

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
importlib.reload(toolsrvt)
import dali_sys
importlib.reload(dali_sys)
from dali_sys import DaliSys


# def write_info(info_list, par_name):
# 	# # write parameter to circuit
# 	for i in info_list:
# 		elem = i[0]
# 		value = str(i[1])
# 		toolsrvt.setup_param_value(elem, par_name, value)


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
board = UnwrapElement(IN[2])  # type: ignore

circuits_to_calculate = toolsrvt.elsys_by_brd(board)[1]
circuits_to_calculate = [circuit for circuit in circuits_to_calculate
	if circuit.CircuitType == Autodesk.Revit.DB.Electrical.CircuitType.Circuit]

if not circuits_to_calculate:
	raise ValueError("No circuits found")

dali_systems = [DaliSys(i) for i in circuits_to_calculate]
DaliSys.get_DALI_controls_info(dali_systems)


# # =========Start transaction
# TransactionManager.Instance.EnsureInTransaction(doc)
# write_info(info_DALIL, "Switching Unit")

# # # =========End transaction
# TransactionManager.Instance.TransactionTaskDone()

# OUT = info_list
OUT = [[i.DALI_control, i.current_sum] for i in dali_systems]
