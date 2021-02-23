import clr
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

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

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *


def ft_to_mm(ft):
	return ft * 304.8


uiapp = DocumentManager.Instance.CurrentUIApplication
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
app = uiapp.Application

reLoad = IN[0]

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
pnt_x1 = obList[0].Location.Point.X
pnt_x2 = obList[1].Location.Point.X
midPointX = (pnt_x1 + pnt_x2) / 2

pnt_y1 = obList[0].Location.Point.Y
pnt_y2 = obList[1].Location.Point.Y
midPointY = (pnt_y1 + pnt_y2) / 2

vectorX = midPointX - obList[2].Location.Point.X
vectorY = midPointY - obList[2].Location.Point.Y
midPointXYZ = XYZ(vectorX, vectorY, 0)

# move element
TransactionManager.Instance.EnsureInTransaction(doc)
ElementTransformUtils.MoveElement(doc, obList[2].Id, midPointXYZ)
TransactionManager.Instance.TransactionTaskDone()
