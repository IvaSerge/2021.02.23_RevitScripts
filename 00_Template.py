import clr
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import os.path

import math

from operator import itemgetter, attrgetter
import string
import re

clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

import System
from System import Array
from System.Collections.Generic import *
import Autodesk.DesignScript as ds

clr.AddReferenceByName('Microsoft.Office.Interop.Excel, Version=11.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c')
from Microsoft.Office.Interop import Excel

System.Threading.Thread.CurrentThread.CurrentCulture = System.Globalization.CultureInfo("en-US")
from System.Runtime.InteropServices import Marshal

clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
from Revit.Elements import *
clr.ImportExtensions(Revit.GeometryConversion)
clr.ImportExtensions(Revit.GeometryReferences)

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView


def ProcessList(_func, _list):
	return map(
		lambda x: ProcessList(_func, x)
		if type(x) == list else _func(x), _list)


def Unwrap(_item):
	if isinstance(_item, list):
		return ProcessList(Unwrap, _item)
	else:
		return UnwrapElement(_item)


# пример для получения типа стены
walltypes = []
# если на входе лист
if isinstance(IN[0], list):
	for i in IN[0]:
		walltypes.append(U(i).WallType)
# в противном случае (это означает, что на входе 1 элемент)
else:
	walltypes = U(IN[0]).WallType
OUT = walltypes


def GetParVal(elem, name):
	value = None
	# custom parameter
	param = elem.LookupParameter(name)
	# check is it a BuiltIn parameter if not found
	if not(param):
		param = elem.get_Parameter(GetBuiltInParam(name))

	# get paremeter Value if found
	try:
		storeType = param.StorageType
		# value = storeType
		if storeType == StorageType.String:
			value = param.AsString()
		elif storeType == StorageType.Integer:
			value = param.AsDouble()
		elif storeType == StorageType.Double:
			value = param.AsDouble()
		elif storeType == StorageType.ElementId:
			value = param.AsValueString()
	except:
		pass
	return value


def GetBuiltInParam(paramName):
	builtInParams = System.Enum.GetValues(BuiltInParameter)
	param = []
	for i in builtInParams:
		if i.ToString() == paramName:
			param.append(i)
			return i


def SetupParVal(elem, name, pValue):
	global doc
	# custom parameter
	param = elem.LookupParameter(name)
	# check is it a BuiltIn parameter if not found
	if not(param):
		try:
			param = elem.get_Parameter(GetBuiltInParam(name)).Set(pValue)
		except:
			pass

	if param:
		try:
			param.Set(pValue)
		except:
			pass
	return elem


def getByCatAndStrParam(_bic, _bip, _val, _isType):
	global doc
	if _isType:
		fnrvStr = FilterStringEquals()
		pvp = ParameterValueProvider(ElementId(int(_bip)))
		frule = FilterStringRule(pvp, fnrvStr, _val, False)
		filter = ElementParameterFilter(frule)
		elem = FilteredElementCollector(doc).\
			OfCategory(_bic).\
			WhereElementIsElementType().\
			WherePasses(filter).\
			ToElements()
	else:
		fnrvStr = FilterStringEquals()
		pvp = ParameterValueProvider(ElementId(int(_bip)))
		frule = FilterStringRule(pvp, fnrvStr, _val, False)
		filter = ElementParameterFilter(frule)
		elem = FilteredElementCollector(doc).\
			OfCategory(_bic).\
			WhereElementIsNotElementType().\
			WherePasses(filter).\
			ToElements()
	return elem


def getTypeByCatFamType(_bic, _fam, _type):
	global doc
	fnrvStr = FilterStringEquals()

	pvpType = ParameterValueProvider(ElementId(int(BuiltInParameter.SYMBOL_NAME_PARAM)))
	pvpFam = ParameterValueProvider(ElementId(int(BuiltInParameter.ALL_MODEL_FAMILY_NAME)))

	fruleF = FilterStringRule(pvpFam, fnrvStr, _fam, False)
	filterF = ElementParameterFilter(fruleF)

	fruleT = FilterStringRule(pvpType, fnrvStr, _type, False)
	filterT = ElementParameterFilter(fruleT)

	filter = LogicalAndFilter(filterT, filterF)

	elem = FilteredElementCollector(doc).\
		OfCategory(_bic).\
		WhereElementIsElementType().\
		WherePasses(filter).\
		FirstElement()
	return elem


def mm_to_ft(mm):
	return 3.2808 * mm / 1000


def ft_to_mm(ft):
	return ft * 304.8


# array = ModelCurveArray() # создание массива Array
# array.Append(UnwrapElement(i)) # положить элементы в массив

# Ids=List[ElementId]() #Icollection в данном случае для ElementId
# Ids.Add(UnwrapElement(i).Id) # добавить элементы в Icollection

# получение всех элементов категории OST_Wire кроме их типов
# wires = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Wire).WhereElementIsNotElementType().ToElements()
# dstype=[]
# for i in wires:
# 	dstype.append(i.ToDSType(True))
# OUT = IN[0].split(‘/’) # разделить данные типа String по символу '/'

# ModelCurve to Line Dynamo
# UnwrapElement(IN[0]).GeometryCurve.ToProtoType()

# Line Dynamo to ModelLine
# ModelCurve.ByCurve(IN[0])

# получение параметра по его BuiltIn значению
# OUT = UnwrapElement(IN[0]).get_Parameter(BuiltInParameter.ELEM_FAMILY_PARAM).AsValueString()
# в зависимости от параметра окончание может быть также AsString() AsDouble()

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

# new.ToDSType(False)
