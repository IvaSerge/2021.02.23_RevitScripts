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

def change_param_values (_elem, p_name_1, p_name_2):
	try:
		p_val_1 = toolsrvt.get_parval(_elem, p_name_1)
		p_val_2 = toolsrvt.get_parval(_elem, p_name_2)
	except:
		return None

	toolsrvt.setup_param_value(_elem, p_name_1, p_val_2)
	toolsrvt.setup_param_value(_elem, p_name_2, p_val_1)

# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView
reload_var = IN[1]  # type: ignore

# Get all instances of category
elems = FilteredElementCollector(doc).\
	OfCategory(BuiltInCategory.OST_SecurityDevices).\
	WhereElementIsNotElementType().\
	ToElements()

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

for elem in elems:
	change_param_values(elem, "TO Rack Floor", "TO Rack Grid")

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = elems
