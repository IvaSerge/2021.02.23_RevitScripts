import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

dir_path = IN[0].DirectoryName  # type: ignore
sys.path.append(dir_path)


# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# ================ Python imports
import System
from System import Array
from System.Collections.Generic import *

import importlib
from importlib import reload

import csv
import re

# ================ local imports
import toolsrvt
reload(toolsrvt)
from toolsrvt import *

import csvreader
reload(csvreader)


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView

reload_IN = IN[1]  # type: ignore
csv_breakers = dir_path + "\\" + IN[2]  # type: ignore
outlist = list()

# ================ get info for circuit breaker settings
cbreakers_list = csvreader.get_breakers_info(csv_breakers)
cb_paramts_to_set = csvreader.csv_to_rvt_elements(cbreakers_list, doc)


# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# ================ set parameters
for i in cb_paramts_to_set:
	if not i:
		continue
	elems = list(i)
	elem_rvt = elems[0]
	p_name = elems[1]
	p_value = elems[2]
	toolsrvt.setup_param_value(elem_rvt, p_name, p_value)

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = cbreakers_list
