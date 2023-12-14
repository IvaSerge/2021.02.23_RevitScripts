"""
Script sets LP parameter for all sheets with that parameter empty
"""
import clr
import sys

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

# ================ local imports
import toolsrvt
reload(toolsrvt)
from toolsrvt import *


def get_par_val_by_list(elem, param_list):
	values = list()
	for param in param_list:
		try:
			param_value = toolsrvt.get_parval(elem, param)
			if param_value is not None:
				values.append([param, param_value])
		except:
			pass
	return values


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView

# =============== IN Block
reload_var = IN[1]  # type: ignore

rvt_sheets = FilteredElementCollector(doc).\
	OfCategory(BuiltInCategory.OST_Sheets).\
	WhereElementIsNotElementType().\
	ToElements()

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

for sht in rvt_sheets:
	lph_current_value = sht.LookupParameter("Planungsphase").AsString()
	toolsrvt.setup_param_value(sht, "Planungsphase", "Ausführungsplanung LPH5")
	
# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

# OUT = param_values
OUT = rvt_sheets
