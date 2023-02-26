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

toolsrvt.doc = doc
toolsrvt.UnwrapElement = UnwrapElement  # type: ignore

# hard coded parameters
circuits_param_to_set = ["RBS_ELEC_CIRCUIT_FRAME_PARAM"]
panel_params_to_set = [
	"_IR(LTPU)", "_tr(LTD)",
	"_Isd(STPU)", "_tsd(STD)",
	"_Ii(INST)",
	"_Ig(GFPU)", "_tg(GFD)"]

header_point = [-0.919769759118699, 1.67170722337784, 0]
body_point = [-0.916488919223686, 1.44502170713041, 0]
shedule_origin = [-1.15591572531952, 1.68093458558256, 0]

header_symbol = type_by_bic_fam_type(
	BuiltInCategory.OST_GenericAnnotation,
	"Panel main FD",
	"Panel main FD")

body_symbol = type_by_bic_fam_type(
	BuiltInCategory.OST_GenericAnnotation,
	"Panel FD",
	"Panel FD")


# get panel
panel_inst = toolsrvt.unwrap(IN[3])  # type: ignore
circuits_all = elsys_by_brd(panel_inst)
circuits_main = circuits_all[0]
circuits = circuits_all[1]


# ================ HEADER diagramm for panel
header_diag = Diagramm()
header_diag.isert_point = XYZ(
	header_point[0],
	header_point[1],
	header_point[2])
header_diag.symbol_type = header_symbol
header_diag.params = [[i, get_parval(panel_inst, i)] for i in panel_params_to_set]

# panel connected from
if circuits_main:
	panel_connected_name = circuits_main.BaseEquipment.Name
	header_diag.params.append(["Panel name", panel_connected_name])
else:
	panel_connected_name = None

# connected from panel - Refer to sheet name
if panel_connected_name:
	# panel_connected_layout = SHEET_NAME inst_by_cat_strparamvalue
	panel_connected_sheet = inst_by_cat_strparamvalue(
		BuiltInCategory.OST_Sheets,
		BuiltInParameter.SHEET_NAME,
		panel_connected_name,
		False)
	if panel_connected_sheet:
		panel_connected_sheet_number = panel_connected_sheet[0].get_Parameter(BuiltInParameter.SHEET_NUMBER).AsString()
		header_diag.params.append(["Reference", panel_connected_sheet_number])

# circuit number
circuits_main_number = circuits_main.CircuitNumber
header_diag.params.append(["RBS_ELEC_CIRCUIT_NUMBER", circuits_main_number])
diagramms_list.append(header_diag)


# ================ BODY diagramms for circuits
for i, circuit in enumerate(circuits):
	body_diag = Diagramm()
	body_diag.params = [[i, get_parval(circuit, i)] for i in circuits_param_to_set]
	step_y = 0.0623365636168
	step_current = step_y * i
	body_diag.isert_point = XYZ(
		body_point[0],
		body_point[1] - step_current,
		body_point[2])
	body_diag.symbol_type = body_symbol
	body_diag.get_circuit_symbol(circuit)
	diagramms_list.append(body_diag)


# ================ SHEET Info
# get sheet
obj_on_sheet = UnwrapElement(IN[2])  # type: ignore
sheet_obj = doc.GetElement(obj_on_sheet.OwnerViewId)

# ================ SHEDULE
# find shedule to be installed
shedule_view = Diagramm.get_shedule_view(doc, panel_inst, sheet_obj)

# find instances to be removed
filter_instance_body = FamilyInstanceFilter(doc, body_symbol.Id)
filter_instance_header = FamilyInstanceFilter(doc, header_symbol.Id)
filter_all = LogicalOrFilter([filter_instance_body, filter_instance_header])
to_remove_id = List[ElementId](sheet_obj.GetDependentElements(filter_all))

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# clean sheet
doc.Delete(to_remove_id)

# create diagramms on sheet
for body_diag in diagramms_list:
	body_diag.instance = body_diag.create_diag_on_sheet(doc, sheet_obj)

doc.Regenerate()

# set parameters
for body_diag in diagramms_list:
	Diagramm.set_parameters(body_diag)

# create shedule instance
if shedule_view:
	shedule_inst = Electrical.PanelScheduleSheetInstance.Create(doc, shedule_view.Id, sheet_obj)
	shedule_inst.Origin = XYZ(shedule_origin[0], shedule_origin[1], shedule_origin[2])

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()


OUT = shedule_view, [i.instance for i in diagramms_list]
