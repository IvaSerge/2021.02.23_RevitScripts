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


def categoryByBICname(_bicString):
	global doc
	bicList = System.Enum.GetValues(BuiltInCategory)
	bic = [i for i in bicList if _bicString == i.ToString()][0]
	return bic


def getInsByBICList(_bicList):
	cat_list = [categoryByBICname(i) for i in _bicList]
	typed_list = List[BuiltInCategory](cat_list)
	filter = ElementMulticategoryFilter(typed_list)
	elements = FilteredElementCollector(doc).WherePasses(filter).\
		WhereElementIsNotElementType().ToElements()
	return elements


def mm_to_ft(mm):
	return 3.2808 * mm / 1000


def ft_to_mm(ft):
	return ft * 304.8


def SetpParVal(elem, name, pValue):
	global doc
	try:
		TransactionManager.Instance.EnsureInTransaction(doc)
		elem.LookupParameter(name).Set(pValue)
		TransactionManager.Instance.TransactionTaskDone()
	except:
		familyName = elem.Symbol.Family.Name
		msg = "There is no parameter to set in Family %s " % (familyName)
		raise ValueError(msg)


def getElevation(_elem):
	global doc
	offset = ft_to_mm(_elem.get_Parameter(
		BuiltInParameter.INSTANCE_FREE_HOST_OFFSET_PARAM)
		.AsDouble())
	return math.ceil((round(offset / 1000, 3) * 100)) / 100


def setElevation(_info):
	elem = _info[0]
	textToSet = str(_info[1])
	SetpParVal(elem, "Высота_установки", textToSet)
	return _info


reload = IN[0]

bicList = [
	"OST_ElectricalFixtures",
	"OST_LightingDevices",
	"OST_LightingFixtures"]

elemList = getInsByBICList(bicList)
elevations = map(getElevation, elemList)
map(setElevation, zip(elemList, elevations))

OUT = elemList
