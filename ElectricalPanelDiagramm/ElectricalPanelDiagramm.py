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
diag_header_point = [-0.968982357543896, 1.67170722337784, 0]
diag_body_point = [-0.965701517648883, 1.44502170713041, 0]
shedule_origin = [-1.20512832374472, 1.68093458558256, 0]

diag_header_symbol = type_by_bic_fam_type(
	BuiltInCategory.OST_GenericAnnotation,
	"Panel main FD",
	"Panel main FD")

diag_body_symbol = type_by_bic_fam_type(
	BuiltInCategory.OST_GenericAnnotation,
	"Panel FD",
	"Panel FD")


elements_to_create = list()

# get panel
panel_inst = toolsrvt.unwrap(IN[3])  # type: ignore
circuits = elsys_by_brd(panel_inst)[1]

# get circuit parameters to transfer to 2D diagramm
for i, circuit in enumerate(circuits):
	diagramm = Diagramm()
	diagramm.params = [[i, get_parval(circuit, i)] for i in circuits_param_to_set]
	step_y = 0.0623365636168
	step_current = step_y * i
	diagramm.isert_point = XYZ(
		diag_body_point[0],
		diag_body_point[1] - step_current,
		diag_body_point[2])
	diagramm.symbol_type = diag_body_symbol
	diagramms_list.append(diagramm)

	# isPanel
	# referTo (layout)


# get sheet
obj_on_sheet = UnwrapElement(IN[2])  # type: ignore
sheet_obj = doc.GetElement(obj_on_sheet.OwnerViewId)


# get 2D diagramms

# set parameters to 2D families

# TODO: Clean the layout

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

for diagramm in diagramms_list:
	diagramm.instance = diagramm.create_diag_on_sheet(doc, sheet_obj)

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

# OUT = dir(UnwrapElement)
OUT = [i.instance for i in diagramms_list]
