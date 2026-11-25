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

clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *


# Import Element wrapper extension methods
clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
clr.ImportExtensions(Revit.GeometryConversion)

# ================ Python imports
import System
from importlib import reload
from operator import itemgetter

# ================ local imports
import toolsrvt
reload(toolsrvt)
# Dynamo function, visible only in this node. Pass it into the module.
toolsrvt.UnwrapElement = UnwrapElement  # type: ignore

import grid
reload(grid)
from grid import *

import inst_info_getter
reload(inst_info_getter)
from inst_info_getter import *

def toPoint(doc, xyz):
	x = toolsrvt.ft_to_mm(doc, xyz.X)
	y = toolsrvt.ft_to_mm(doc, xyz.Y)
	z = toolsrvt.ft_to_mm(doc, xyz.Z)
	return Geometry.Point.ByCoordinates(x, y, z)


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView

reload_IN = IN[1]  # type: ignore

if isinstance(IN[2], str):  # type: ignore
	# there is category name
	bic = System.Enum.Parse(BuiltInCategory, IN[2])  # type: ignore
	rvt_instances = FilteredElementCollector(doc).\
		OfCategory(bic).\
		WhereElementIsNotElementType().\
		ToElements()
else:
	toolsrvt.UnwrapElement = UnwrapElement  # type: ignore
	rvt_instances = toolsrvt.flatten_list(toolsrvt.unwrap(IN[2]))  # type: ignore

grid.find_grid_intersection_points(doc)

params_to_set = []
for rvt_inst in rvt_instances:
	shortest_grid_name = grid.get_nearest_grid_by_instance(rvt_inst)
	try:
		inst_level = inst_info_getter.get_level_name(rvt_inst)
	except:
		inst_level = "NA"
	if inst_level is None:
		inst_level = "NA"
	if shortest_grid_name is None:
		shortest_grid_name = "NA"
	params_to_set.append([rvt_inst, "TO Grid", shortest_grid_name])
	params_to_set.append([rvt_inst, "TO Level", inst_level])
	# circuit_parameters = inst_info_getter.get_circuit_params(rvt_inst, inst_level, shortest_grid_name)
	# if circuit_parameters:
	# 	params_to_set.extend(circuit_parameters)

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

for param_info in params_to_set:
	try:
		toolsrvt.setup_param_value(param_info[0], param_info[1], param_info[2])
	except Exception as e:
		elem_id = param_info[0].Id.IntegerValue
		error_text = f"check the element - {elem_id}, {param_info[1]}, {param_info[2]}"
		print(error_text)
		raise ValueError(error_text) from e

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = params_to_set
