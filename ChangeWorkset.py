import clr
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

import System

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

doc = DocumentManager.Instance.CurrentDBDocument


def ProcessList(_func, _list):
	return map(
		lambda x: ProcessList(_func, x)
		if type(x) == list else _func(x), _list)


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
	return None


def SetupParVal(elem, name, pValue):
	global doc
	# custom parameter
	param = elem.LookupParameter(name)
	# check is it a BuiltIn parameter if not found
	if not(param):
		param = elem.get_Parameter(GetBuiltInParam(name)).Set(pValue)
	else:
		param.Set(pValue)

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


def setWorkset(elem_list, workset_name):
	"""
	Change workset of elements

	:global:
		workset_rvt - [Autodesk.Revit.DB.Workset]
			list of filtered worksets
	:args:
		elem_list - list()
			List of Revit elements
		workset_name - str()
			name of workset to be set
	:return:
			workset name
	"""
	# check if list is empty
	if not(elem_list):
		return None

	# get workset instance by name
	wokrset_inst = [
		i for i in workset_rvt
		if i.Name == workset_name]
	wokrset_id = int(wokrset_inst[0].Id.ToString())

	set_param = lambda x: SetupParVal(
		x,
		"ELEM_PARTITION_PARAM",
		wokrset_id)
	map(set_param, elem_list)

	return wokrset_inst[0].Name


workset_list = list()
workset_list.append("00_Ebenen und Raster")
workset_list.append("01_LINK_Architektur")
workset_list.append("01_LINK_Elektro")
workset_list.append("01_LINK_Heizung_Kälte")
workset_list.append("01_LINK_Lüftung")
workset_list.append("01_LINK_Sanitär")
workset_list.append("440_Elektro_Anlagen_Starkstrom")
workset_list.append("440_Elektro_Kabeltrassen Starkstrom")
workset_list.append("450_Elektro_Kabeltrassen_Schwachstrom")
workset_list.append("450_Eletro_Anlagen_Schwachstrom")

workset_rvt = [
	i for i in FilteredWorksetCollector(doc) if
	i.Name in workset_list]

# chekc if all standard worksets exists in project
if len(workset_rvt) != len(workset_list):
	raise ValueError('Check worksets!')

# RVT model objects
levelElem = FilteredElementCollector(doc)\
	.OfCategory(BuiltInCategory.OST_Levels)\
	.WhereElementIsNotElementType()\
	.ToElements()

gridElem = FilteredElementCollector(doc)\
	.OfCategory(BuiltInCategory.OST_Grids)\
	.WhereElementIsNotElementType()\
	.ToElements()

linkElem = FilteredElementCollector(doc)\
	.OfCategory(BuiltInCategory.OST_RvtLinks)\
	.WhereElementIsNotElementType()\
	.ToElements()

# sort linkElem
link_ELT = [i for i in linkElem if "_ELT" in i.Name]
link_HLKS = [i for i in linkElem if "_HLKS" in i.Name]
link_Arch = [i for i in linkElem if all([
	i not in link_ELT,
	i not in link_HLKS])]

electroElem = FilteredElementCollector(doc)\
	.OfCategory(BuiltInCategory.OST_ElectricalFixtures)\
	.WhereElementIsNotElementType()\
	.ToElements()

leuchten = FilteredElementCollector(doc)\
	.OfCategory(BuiltInCategory.OST_LightingFixtures)\
	.WhereElementIsNotElementType()\
	.ToElements()

lichtschalter = FilteredElementCollector(doc)\
	.OfCategory(BuiltInCategory.OST_LightingDevices)\
	.WhereElementIsNotElementType()\
	.ToElements()

electroBoards = FilteredElementCollector(doc)\
	.OfCategory(BuiltInCategory.OST_ElectricalEquipment)\
	.WhereElementIsNotElementType()\
	.ToElements()

all_elektro = list()
addToList = lambda x: all_elektro.append(x)
map(addToList, electroElem)
map(addToList, leuchten)
map(addToList, lichtschalter)
map(addToList, electroBoards)

bmaElem = FilteredElementCollector(doc)\
	.OfCategory(BuiltInCategory.OST_FireAlarmDevices)\
	.WhereElementIsNotElementType()\
	.ToElements()

dataElem = FilteredElementCollector(doc)\
	.OfCategory(BuiltInCategory.OST_DataDevices)\
	.WhereElementIsNotElementType()\
	.ToElements()

NotRuf = FilteredElementCollector(doc)\
	.OfCategory(BuiltInCategory.OST_NurseCallDevices)\
	.WhereElementIsNotElementType()\
	.ToElements()

all_data = list()
addToList = lambda x: all_data.append(x)
map(addToList, bmaElem)
map(addToList, dataElem)
map(addToList, NotRuf)

# Kabeltrasse und formteile
kabTr = FilteredElementCollector(doc)\
	.OfCategory(BuiltInCategory.OST_CableTray)\
	.WhereElementIsNotElementType()\
	.ToElements()

kabForm = FilteredElementCollector(doc)\
	.OfCategory(BuiltInCategory.OST_CableTrayFitting)\
	.WhereElementIsNotElementType()\
	.ToElements()

all_kab = list()
addToList = lambda x: all_kab.append(x)
map(addToList, kabTr)
map(addToList, kabForm)

# filtering Kabeltrassen Starkstrom
all_kab_elektro = list()
filter_list = ["_MS", "_SV", "_NS"]

addToList = lambda x: all_kab_elektro.append(x)\
	if any([
		True if i in GetParVal(x, "ELEM_TYPE_PARAM")
		else False for i in filter_list])\
	else None

map(addToList, all_kab)

# filtering Kabeltrassen Starkstrom
all_kab_dat = list()
filter_list = ["_SS"]

addToList = lambda x: all_kab_dat.append(x)\
	if any([
		True if i in GetParVal(x, "ELEM_TYPE_PARAM")
		else False for i in filter_list])\
	else None

map(addToList, all_kab)

TransactionManager.Instance.EnsureInTransaction(doc)

lvls = setWorkset(levelElem, "00_Ebenen und Raster")
grids = setWorkset(gridElem, "00_Ebenen und Raster")
links_ELT = setWorkset(link_ELT, "01_LINK_Elektro")
links_HLKS = setWorkset(link_HLKS, "01_LINK_Heizung_Kälte")
links_Arch = setWorkset(link_Arch, "01_LINK_Architektur")
all_elt = setWorkset(all_elektro, "440_Elektro_Anlagen_Starkstrom")
all_dat = setWorkset(all_data, "450_Eletro_Anlagen_Schwachstrom")
kab_elt = setWorkset(all_kab_elektro, "440_Elektro_Kabeltrassen Starkstrom")
kab_dat = setWorkset(all_kab_dat, "450_Elektro_Kabeltrassen_Schwachstrom")

TransactionManager.Instance.TransactionTaskDone()

OUT = all_kab_dat
