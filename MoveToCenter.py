import clr

import sys
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import System
from System import Array
from System.Collections.Generic import *

import itertools
import math

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument

# ================ Revit imports
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

# Import Element wrapper extension methods
clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
clr.ImportExtensions(Revit.GeometryConversion)


def ft_to_mm(ft):
	return ft * 304.8


def toPoint(xyz):
	x = ft_to_mm(xyz.X)
	y = ft_to_mm(xyz.Y)
	z = ft_to_mm(xyz.Z)
	return Point.ByCoordinates(x, y, z)


class Vec():
	def __init__(self, start, end):
		"""
		Vector by start-end points all
		"""
		vector_x = end.X - start.X
		vector_y = end.Y - start.Y
		vector_z = end.Z - start.Z

		self.start = start
		self.end = end
		self.coord = XYZ(vector_x, vector_y, vector_z)
		basis = Autodesk.Revit.DB.XYZ.BasisX
		self.direction = basis.AngleTo(self.coord)

	def num_multiply(self, num):
		vector_x = self.coord.X * num
		vector_y = self.coord.Y * num
		vector_z = self.coord.Z * num
		return XYZ(vector_x, vector_y, vector_z)


uiapp = DocumentManager.Instance.CurrentUIApplication
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
app = uiapp.Application

reLoad = IN[0]  # type: ignore
distance_k = IN[1]  # type: ignore

ob1 = uidoc.Selection.PickObject(
	Autodesk.Revit.UI.Selection.ObjectType.Element,
	"Selection of two elements")

ob2 = uidoc.Selection.PickObject(
	Autodesk.Revit.UI.Selection.ObjectType.Element,
	"Selection of two elements")

selob = list()
selob.append(ob1)
selob.append(ob2)

lastob = uidoc.Selection.PickObject(
	Autodesk.Revit.UI.Selection.ObjectType.Element,
	"Selection of two elements")

refList = list()
map(lambda x: refList.append(x), selob)
refList.append(lastob)

obList = list()
map(lambda x: obList.append(doc.GetElement(x.ElementId)), refList)

# new point coordinates calculation
start = obList[0].Location.Point
start_xyz = XYZ(start.X, start.Y, 0)
end = obList[1].Location.Point
end_xyz = XYZ(end.X, end.Y, 0)
obj_point = obList[2].Location.Point
obj_point = XYZ(obj_point.X, obj_point.Y, 0)

vector_start_end = Vec(start, end)
new_vector = vector_start_end.num_multiply(distance_k)
new_xyz = XYZ(start.X + new_vector.X,
	start.Y + new_vector.Y,
	0)

move_vector = Vec(obj_point, new_xyz).coord

# move element
TransactionManager.Instance.EnsureInTransaction(doc)
ElementTransformUtils.MoveElement(doc, obList[2].Id, move_vector)
TransactionManager.Instance.TransactionTaskDone()

OUT = move_vector
