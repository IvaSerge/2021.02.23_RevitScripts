import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

dir_path = IN[0].DirectoryName  # type: ignore
sys.path.append(dir_path)


# ================ Revit imports
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# ================ Python imports
from System import Array
from System.Collections.Generic import *
from importlib import reload
import re

# ================ local imports
import toolsrvt
from toolsrvt import *

# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView
reload_var = IN[1]  # type: ignore
category_str = IN[2]  # type: ignore

rvt_cat = toolsrvt.category_by_bic_name(doc, category_str)
rvt_elems = FilteredElementCollector(doc).\
	OfCategory(rvt_cat.BuiltInCategory).\
	WhereElementIsNotElementType().\
	ToElements()
rvt_elems.sort(key=lambda x: x.Id.IntegerValue)
set_list = []
for i, elem in enumerate(rvt_elems):
	set_list.append([elem, i])

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

for elems in set_list:
	toolsrvt.setup_param_value(
		elems[0],
		"DOOR_NUMBER",
		str(elems[1])
	)

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = set_list
