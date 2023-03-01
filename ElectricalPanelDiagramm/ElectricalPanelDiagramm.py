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
diagramms_list = list()
items_on_sheet_to_remove = list()
pairs_list = list()

toolsrvt.doc = doc
toolsrvt.UnwrapElement = UnwrapElement  # type: ignore

Diagramm.header_symbol = toolsrvt.type_by_bic_fam_type(
	doc,
	BuiltInCategory.OST_GenericAnnotation,
	"Panel main FD",
	"Panel main FD")

Diagramm.body_symbol = toolsrvt.type_by_bic_fam_type(
	doc,
	BuiltInCategory.OST_GenericAnnotation,
	"Panel FD",
	"Panel FD")

Diagramm.foot_symbol = toolsrvt.type_by_bic_fam_type(
	doc,
	BuiltInCategory.OST_GenericAnnotation,
	"Panel FD_Footer",
	"Panel FD_Footer")

# ================ IN DATA
reload_obj = IN[1]  # type: ignore
# update_all
update_all = IN[2]  # type: ignore

if not update_all:
	# get sheet
	obj_on_sheet = UnwrapElement(IN[3])  # type: ignore
	sheet_inst = doc.GetElement(obj_on_sheet.OwnerViewId)
	# get panel
	panel_inst = toolsrvt.unwrap(IN[4])  # type: ignore
	pairs_list.append([panel_inst, sheet_inst])
	# find shedule to be installed
	shedule_view = Diagramm.get_shedule_view(doc, panel_inst, sheet_inst)

else:
	pairs_list = diag.get_pairs(doc)
	shedule_view = None


for pair in pairs_list:
	panel_inst = pair[0]
	sheet_inst = pair[1]

	# ================ Header info
	header_diag = Diagramm(sheet_inst)
	header_diag.get_header_info(panel_inst)
	diagramms_list.append(header_diag)

	# ================ Body info
	body_diag_list = Diagramm.get_body_info(sheet_inst, panel_inst)
	diagramms_list.extend(body_diag_list)

	# ================ Footer info
	footer_diag_list = Diagramm.get_footer_info(sheet_inst, panel_inst)
	diagramms_list.append(footer_diag_list)

	# ================ Remove items on sheet
	items_on_sheet_to_remove.extend(Diagramm.get_ID_to_remove(sheet_inst))


# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# clean items on sheet(s)
for item in items_on_sheet_to_remove:
	doc.Delete(item)

# create diagramm on sheet only for
for diagramm in diagramms_list:
	diagramm.instance = diagramm.create_diag_on_sheet()

doc.Regenerate()

# # set parameters
for body_diag in diagramms_list:
	Diagramm.set_parameters(body_diag)

# create shedule instance
if shedule_view:
	shedule_inst = Electrical.PanelScheduleSheetInstance.Create(doc, shedule_view.Id, sheet_inst)
	shedule_inst.Origin = XYZ(
		Diagramm.shedule_origin[0],
		Diagramm.shedule_origin[1],
		Diagramm.shedule_origin[2])

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()


# OUT = shedule_view, [i.instance for i in diagramms_list]
OUT = diagramms_list[2].params
