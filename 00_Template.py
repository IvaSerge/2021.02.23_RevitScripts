import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

clr.AddReferenceByName('Microsoft.Office.Interop.Excel, Version=11.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c')
from Microsoft.Office.Interop import Excel

import System
from System import Array
from System.Collections.Generic import *

System.Threading.Thread.CurrentThread.CurrentCulture = System.Globalization.CultureInfo("en-US")
from System.Runtime.InteropServices import Marshal

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# ================ Dynamo imports
clr.AddReference('ProtoGeometry')
import Autodesk.DesignScript as ds
from ds.Geometry import *

clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
from Revit.Elements import *
clr.ImportExtensions(Revit.GeometryConversion)
clr.ImportExtensions(Revit.GeometryReferences)

# ================ Python imports
import os.path
import math
import string
import re
import operator
from operator import itemgetter, attrgetter
import itertools

global doc
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView


def process_list(_func, _list):
	return map(
		lambda x: process_list(_func, x)
		if type(x) == list else _func(x), _list)


def unwrap(_item):
	if isinstance(_item, list):
		return process_list(unwrap, _item)
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


def flatten_list(data):
	# iterating over the data
	list_in_progress = data
	list_found = True

	while list_found:
		flat_list = list()
		list_found = False
		for i in list_in_progress:
			if isinstance(i, list):
				list_found = True
				map(lambda x: flat_list.append(x), i)
			else:
				flat_list.append(i)
		list_in_progress = [x for x in flat_list]

	return list_in_progress


def get_parval(elem, name):
	"""Get parametr value

	args:
		elem - family instance or type
		name - parameter name
	return:
		value - parameter value
	"""

	value = None
	# custom parameter
	param = elem.LookupParameter(name)
	# check is it a BuiltIn parameter if not found
	if not(param):
		param = elem.get_Parameter(get_bip(name))

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


def get_bip(paramName):
	builtInParams = System.Enum.GetValues(BuiltInParameter)
	param = []
	for i in builtInParams:
		if i.ToString() == paramName:
			param.append(i)
			return i


def category_by_bic_name(_bicString):
	global doc
	bicList = System.Enum.GetValues(BuiltInCategory)
	bic = [i for i in bicList if _bicString == i.ToString()][0]
	return GetCategory(doc, bic)


def param_by_cat(_bic, _name):
	"""Get parametr in

	args:
		_bic (BuiltiInCategory.OST_xxx): category
		_name (str): parameter name
	return:
		param (Autodesk.Revit.DB.Parameter) - parameter
	"""
	# check Type parameter
	elem = FilteredElementCollector(doc).\
		OfCategory(_bic).\
		WhereElementIsElementType().\
		FirstElement()
	param = elem.LookupParameter(_name)
	if param:
		return param

	# check instance parameter
	# ATTENTION! instance is first in!
	# Be sure that all instances has the parameter.
	elem = FilteredElementCollector(doc).\
		OfCategory(_bic).\
		WhereElementIsNotElementType().\
		FirstElement()
	param = elem.LookupParameter(_name)
	if param:
		return param

	# Not found
	return None


def setup_param_value(elem, name, pValue):
	# custom parameter
	param = elem.LookupParameter(name)
	# check is it a BuiltIn parameter if not found
	if not(param):
		try:
			param = elem.get_Parameter(get_bip(name)).Set(pValue)
		except:
			pass

	if param:
		try:
			param.Set(pValue)
		except:
			pass
	return elem


def inst_by_cat_strparamvalue(_bic, _bip, _val, _isType):
	"""Get all family instances by category and parameter value

		args:
		_bic - BuiltInCategory.OST_xxx
		_bip - BuiltInParameter

		return:
		Autodesk.Revit.DB.FamilySymbol
	"""
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


def type_by_bic_fam_type(_bic, _fnam, _tnam):
	"""Get Type by family category, family name and type

		args:
		_bic: BuiltInCategory.OST_xxx
		_fnam (str): family name
		_tnam (str): type name

		return:
		Autodesk.Revit.DB.FamilySymbol
	"""

	fnrvStr = FilterStringEquals()

	pvpType = ParameterValueProvider(ElementId(int(BuiltInParameter.SYMBOL_NAME_PARAM)))
	pvpFam = ParameterValueProvider(ElementId(int(BuiltInParameter.ALL_MODEL_FAMILY_NAME)))

	fruleF = FilterStringRule(pvpFam, fnrvStr, _fnam, False)
	filterF = ElementParameterFilter(fruleF)

	fruleT = FilterStringRule(pvpType, fnrvStr, _tnam, False)
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


def elsys_by_brd(_brd):
	"""Get all systems of electrical board.

		args:
		_brd - electrical board FamilyInstance

		return list(1, 2) where:
		1 - main electrical circuit
		2 - list of connectet low circuits
	"""
	allsys = _brd.MEPModel.ElectricalSystems
	lowsys = _brd.MEPModel.AssignedElectricalSystems
	if lowsys:
		lowsysId = [i.Id for i in lowsys]
		mainboardsysLst = [i for i in allsys if i.Id not in lowsysId]
		if len(mainboardsysLst) == 0:
			mainboardsys = None
		else:
			mainboardsys = mainboardsysLst[0]
		lowsys = [i for i in allsys if i.Id in lowsysId]
		lowsys.sort(key=lambda x: float(get_parval(x, "RBS_ELEC_CIRCUIT_NUMBER")))
		return mainboardsys, lowsys
	else:
		return [i for i in allsys][0], None


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
