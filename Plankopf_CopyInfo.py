import clr
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

import System
from System import Enum

doc = DocumentManager.Instance.CurrentDBDocument


def ProcessList(_func, _list):
	return map(lambda x: ProcessList(_func, x) if type(x) == list else _func(x), _list)


def Unwrap(_item):
	if isinstance(_item, list):
		return ProcessList(Unwrap, _item)
	else:
		return UnwrapElement(_item)  # type: ignore


def GetParVal(elem, name):
	# Параметр пользовательский
	try:
		param = elem.LookupParameter(name)
		storeType = param.StorageType
		if storeType == StorageType.String:
			value = elem.LookupParameter(name).AsString()
		elif storeType == StorageType.Integer:
			value = elem.LookupParameter(name).AsDouble()
		elif storeType == StorageType.Double:
			value = elem.LookupParameter(name).AsDouble()
	# Параметр встроенный
	except:
		bip = GetBuiltInParam(name)
		storeType = elem.get_Parameter(bip).StorageType
		if storeType == StorageType.String:
			value = elem.get_Parameter(bip).AsString()
		elif storeType == StorageType.Integer:
			value = elem.get_Parameter(bip).AsDouble()
		elif storeType == StorageType.Double:
			value = elem.get_Parameter(bip).AsDouble()
	return value


def GetBuiltInParam(paramName):
	builtInParams = System.Enum.GetValues(BuiltInParameter)
	param = []

	for i in builtInParams:
		if i.ToString() == paramName:
			param.append(i)
			break
		else:
			continue
	return param[0]


def SetpParVal(elem, name, pValue):
	global doc
	elem.LookupParameter(name).Set(pValue)
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


ElemFrom = Unwrap(IN[0])  # type: ignore
ElemFrom_Sheet = doc.GetElement(ElemFrom.OwnerViewId)

ElemTo = Unwrap(IN[1])  # type: ignore
ElemTo_Sheet = doc.GetElement(ElemTo.OwnerViewId)
reload = IN[2]  # type: ignore
pList_Sheet = list()
pList_Title = list()
ignorParamsList = [
	"SHEET_NAME",
	"VIEWER_SHEET_NUMBER",
	"SHEET_NUMBER",
	"VIEW_TYPE",
	"ELEM_FAMILY_AND_TYPE_PARAM",
	"VIEW_FAMILY_AND_TYPE_SCHEDULES",
	"ALL_MODEL_FAMILY_NAME",
	"VIEW_FAMILY_SCHEDULES",
	"VIEW_FAMILY",
	"VIEW_FAMILY_SCHEDULES",
	"SYMBOL_NAME_PARAM",
	"ELEM_TYPE_PARAM",
	"VIEW_TYPE_SCHEDULES",
	"SHEET_FILE_PATH",
	"MC Page Number",
	"MC Number of Pages",
	"MC Panel Code",
	"PB_Sub Gewerk", ]

SheetBic = "OST_Sheets"
SheetNum = "SHEET_NUMBER"

# =========Params for sheets
paramList_Sheet = ElemFrom_Sheet.Parameters
for param in paramList_Sheet:
	storeType = param.StorageType
	if storeType == StorageType.String:
		# check if parameter Built-in
		parBIP = param.Definition.BuiltInParameter.ToString()
		if parBIP == "INVALID":
			checkName = param.Definition.Name
		else:
			checkName = parBIP
		if checkName not in ignorParamsList:
			pName = param.Definition.Name
			pValue = param.AsString()
			pList_Sheet.append([pName, pValue])

# =========Params for Title
paramList_Title = ElemFrom.Parameters
for param in paramList_Title:
	storeType = param.StorageType

	# check if param is boolean
	isBool = all([storeType == StorageType.Integer,
		param.Definition.ParameterType == ParameterType.YesNo])

	if any([
		storeType == StorageType.String,
		isBool,
		storeType == StorageType.ElementId]):
		# check if parameter Built-in
		parBIP = param.Definition.BuiltInParameter.ToString()
		if parBIP == "INVALID":
			checkName = param.Definition.Name
		else:
			checkName = parBIP

		if checkName not in ignorParamsList:
			pName = param.Definition.Name
			if isBool:
				pValue = param.AsInteger()
			elif storeType == StorageType.String:
				pValue = param.AsString()
			elif storeType == StorageType.ElementId:
				pValue = param.AsElementId()
			else:
				pass
			pList_Title.append([pName, pValue])

# find Legends on view
try:
	allVports = [doc.GetElement(x) for x in ElemFrom_Sheet.GetAllViewports()]
	allViews = [doc.GetElement(x.ViewId) for x in allVports]
	allCoords = [x.GetBoxCenter() for x in allVports]
	legendViews = [x for x in zip(allViews, allCoords) if x[0].ViewType == ViewType.Legend]
except:
	legendViews = None

# All elements on view
elems_on_view = FilteredElementCollector(doc, ElemFrom_Sheet.Id).ToElementIds()

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)


# Set parameters of sheet
for param in pList_Sheet:
	pName = param[0]
	pValue = param[1]
	try:
		SetpParVal(ElemTo_Sheet, pName, pValue)
	except:
		None

# Set parameters of Title block
for param in pList_Title:
	pName = param[0]
	pValue = param[1]
	try:
		SetpParVal(ElemTo, pName, pValue)
	except:
		None

# CreateLegends
if legendViews:
	for legView in legendViews:
		viewId = legView[0].Id
		insertPoint = legView[1]
		try:
			Viewport.Create(
				doc,
				ElemTo_Sheet.Id,
				viewId,
				insertPoint)
		except:
			None

# Copy all elements on view
# if elems_on_view:
# 	tr_form = ElementTransformUtils.GetTransformFromViewToView(
# 		ElemFrom_Sheet,
# 		ElemTo_Sheet)
# 	copy_opt = CopyPasteOptions()
# 	ElementTransformUtils.CopyElements(
# 		ElemFrom_Sheet,
# 		elems_on_view,
# 		ElemTo_Sheet,
# 		tr_form,
# 		copy_opt)


# =========End transaction

TransactionManager.Instance.TransactionTaskDone()

OUT = elems_on_view
