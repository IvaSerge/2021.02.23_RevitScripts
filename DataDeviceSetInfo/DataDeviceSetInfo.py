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

clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *


# Import Element wrapper extension methods
clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
clr.ImportExtensions(Revit.GeometryConversion)

# ================ Python imports
import collections
from collections import deque

import importlib
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
	return Autodesk.DesignScript.Geometry.Point.ByCoordinates(x, y, z)


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView

reload_IN = IN[1]  # type: ignore
rvt_data_device = UnwrapElement(IN[2])  # type: ignore

rvt_data_device_point = rvt_data_device.Location.Point

all_grids = FilteredElementCollector(doc).\
	OfCategory(BuiltInCategory.OST_Grids).\
	WhereElementIsNotElementType().\
	ToElements()

all_intersection_points = dict()
obj_grids = [grid(i) for i in all_grids]
for grd in obj_grids:
	grid_intersections = grd.get_intersection_points(obj_grids)
	all_intersection_points.update(grid_intersections)

# get all distances list
distance_list = list()
for key, value in all_intersection_points.items():
	distance = rvt_data_device_point.DistanceTo(value)
	distance_list.append([key, distance])

distance_list.sort(key=itemgetter(1))
shortest_grid_name = distance_list[0][0]

# # =========Start transaction
# TransactionManager.Instance.EnsureInTransaction(doc)


# # =========End transaction
# TransactionManager.Instance.TransactionTaskDone()

# OUT = [toPoint(doc, i) for i in obj_grids[0].intersections]
# OUT = [[key, value] for key, value in obj_grids[0].intersections]
OUT = shortest_grid_name
