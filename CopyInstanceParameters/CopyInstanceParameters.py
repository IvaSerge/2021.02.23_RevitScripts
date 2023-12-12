"""
Script copies parameter values from family to other family or list of families.
Families may be selected inside Dynamo or using API.
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


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView

# =============== IN Block
reload_var = IN[1]  # type: ignore
copy_from = IN[2]  # type: ignore
copy_to = IN[3]  # type: ignore
settings_worksets = IN[4]  # type: ignore
settings_parameters = IN[5]  # type: ignore

# Check selection in Dynamo
if copy_to:
	elems_list = copy_to

# Propose selection via Revit API
else:
	rvt_ref = uidoc.Selection.PickObject(
		Autodesk.Revit.UI.Selection.ObjectType.Element, "")
	elems_list = [doc.GetElement(rvt_ref.ElementId)]

# TODO: apply wokrset
# TODO: apply phase
# TODO: apply parameters

OUT = elems_list
