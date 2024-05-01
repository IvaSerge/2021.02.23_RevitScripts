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

import grid
reload(grid)
from grid import *


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

if not isinstance(IN[2], str):  # type: ignore
	rvt_instances = [UnwrapElement(IN[2])]  # type: ignore
else:
	# # there is category
	bic = System.Enum.Parse(BuiltInCategory, IN[2])  # type: ignore
	rvt_instances = FilteredElementCollector(doc).\
		OfCategory(bic).\
		WhereElementIsNotElementType().\
		ToElements()

grid.find_grid_intersection_points(doc)

params_to_set = []
for rvt_inst in rvt_instances:
	shortest_grid_name = grid.get_nearest_grid_by_instance(rvt_inst)
	params_to_set.append([rvt_inst, "TO Grid", shortest_grid_name])

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

for param_info in params_to_set:
	toolsrvt.setup_param_value(param_info[0], param_info[1], param_info[2])

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = params_to_set
