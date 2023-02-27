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

# ================ local imports
import toolsrvt
reload(toolsrvt)
from toolsrvt import *
import diag
reload(diag)
from diag import *

# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView
reload = IN[1]  # type: ignore
diagramms_list = list()
items_on_sheet_to_remove = list()

toolsrvt.doc = doc
toolsrvt.UnwrapElement = UnwrapElement  # type: ignore

# ================ IN DATA
# get panel
panel_inst = toolsrvt.unwrap(IN[3])  # type: ignore
# get sheet
obj_on_sheet = UnwrapElement(IN[2])  # type: ignore
sheet_obj = doc.GetElement(obj_on_sheet.OwnerViewId)

header_diag = Diagramm
header_diag = Diagramm.get_header_info(panel_inst)
diagramms_list.append(header_diag)
body_diag_list = Diagramm.get_body_info(panel_inst)
diagramms_list.extend(body_diag_list)

# ================ SHEDULE
# find shedule to be installed
shedule_view = Diagramm.get_shedule_view(doc, panel_inst, sheet_obj)
items_on_sheet_to_remove = Diagramm.get_ID_to_remove(sheet_obj)


# # =========Start transaction
# TransactionManager.Instance.EnsureInTransaction(doc)

# # clean items on sheet(s)
# doc.Delete(items_on_sheet_to_remove)

# # create diagramms on sheet
# for body_diag in diagramms_list:
# 	body_diag.instance = body_diag.create_diag_on_sheet(doc, sheet_obj)

# doc.Regenerate()

# # set parameters
# for body_diag in diagramms_list:
# 	Diagramm.set_parameters(body_diag)

# # create shedule instance
# if shedule_view:
# 	shedule_inst = Electrical.PanelScheduleSheetInstance.Create(doc, shedule_view.Id, sheet_obj)
# 	shedule_inst.Origin = XYZ(
# 		Diagramm.shedule_origin[0],
# 		Diagramm.shedule_origin[1],
# 		Diagramm.shedule_origin[2])

# # =========End transaction
# TransactionManager.Instance.TransactionTaskDone()


# OUT = shedule_view, [i.instance for i in diagramms_list]
OUT = items_on_sheet_to_remove
