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
reload_var = IN[1]  # type: ignore
sheet_number = IN[2]  # type: ignore

# get sheet by name
bip_sheet_number = get_bip("SHEET_NUMBER")
sheet_rvt = inst_by_cat_strparamvalue(doc, BuiltInCategory.OST_Sheets, bip_sheet_number, sheet_number, False)[0] # type: ViewSheet
sheet_id = sheet_rvt.Id

# get all revision clouds to be deleted
revision_cloud_ids = sheet_rvt.GetAllRevisionCloudIds()

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# Set empty list to remove all
empty_list = List[ElementId]()
sheet_rvt.SetAdditionalRevisionIds(empty_list)

# Remove revision
if revision_cloud_ids:
	for cloud in revision_cloud_ids:
		doc.Delete(cloud)

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = sheet_rvt
