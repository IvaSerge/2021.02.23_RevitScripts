import clr
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager


def mm_to_ft(mm):
	"""
	Converts millimeter to foot

		:param mm: value to be converted
		:type mm: float
		:return: converted millimeters to feet
		:rtype: float
	"""
	return 3.2808 * mm / 1000


def ft_to_mm(ft):
	return ft * 304.8


def coordInLink(_startPnt):
	"""Converts active doc point coordinate to linked doc local coordinate"""
	global docOrigin
	x_new = _startPnt.X - docOrigin.X
	y_new = _startPnt.Y - docOrigin.Y
	z_new = _startPnt.Z - docOrigin.Z
	xyz_new = XYZ(x_new, y_new, z_new)
	return xyz_new


def infoToSpace(_info):
	global doc
	_room = _info[1]
	_space = _info[0]
	if not(_room):
		rmName = "N/A"
		rmNumber = "N/A"
		out = "N/A"
	else:
		rmName = _room.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()
		rmNumber = _room.get_Parameter(BuiltInParameter.ROOM_NUMBER).AsString()
		out = _space

	TransactionManager.Instance.EnsureInTransaction(doc)

	_space.get_Parameter(BuiltInParameter.ROOM_NAME).Set(rmName)
	_space.get_Parameter(BuiltInParameter.ROOM_NUMBER).Set(rmNumber)
	TransactionManager.Instance.TransactionTaskDone()
	return out


doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application

link = UnwrapElement(IN[1])
docL = link.GetLinkDocument()
docOrigin = link.GetTransform().Origin

spaces = FilteredElementCollector(doc)\
	.OfCategory(BuiltInCategory.OST_MEPSpaces)\
	.WhereElementIsNotElementType()\
	.ToElements()

roomL = FilteredElementCollector(docL)\
	.OfCategory(BuiltInCategory.OST_Rooms)\
	.WhereElementIsNotElementType()\
	.FirstElement()

rmId = roomL.get_Parameter(BuiltInParameter.ROOM_PHASE_ID).AsElementId()
rmPhase = docL.GetElement(rmId)

spacePnts = list()
for space in spaces:
	try:
		spacePnt = space.Location.Point
		spacePnts.append(spacePnt)
	except:
		pass

pntsInLink = [coordInLink(x) for x in spacePnts]
roomsBySpace = [docL.GetRoomAtPoint(x, rmPhase) for x in pntsInLink]
roomsAndSpaces = zip(spaces, roomsBySpace)
newSpaces = [infoToSpace(x) for x in roomsAndSpaces]

OUT = docL
