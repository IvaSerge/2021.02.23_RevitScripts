
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
# pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
# sys.path.append(pyt_path)
sys.path.append(IN[0].DirectoryName)  # type: ignore

import System
from System import Array
from System.Collections.Generic import *

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager


def get_parval(elem, name):
	"""Get parametr value

	args:
		elem - family instance or type\n
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


def setup_param_value(elem, name, pValue):

	# check element staus
	elem_status = WorksharingUtils.GetCheckoutStatus(doc, elem.Id)

	if elem_status == CheckoutStatus.OwnedByOtherUser:
		return None

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


def get_first_elem_of_system(_el_sys):
	"""Get first family instances of electrical system

		args:
		_el_sy: Electrical system

		return:
		Family instance
	"""
	first_elem = None
	elements = [i for i in _el_sys.Elements]
	if elements:
		first_elem = elements[0]

	return first_elem


def inst_by_cat_strparamvalue(_bic, _bip, _val, _isType):
	"""Get all family instances by category and parameter value

		args:
		_bic: BuiltInCategory.OST_xxx
		_bip: BuiltInParameter

		return:
		list()[Autodesk.Revit.DB.FamilySymbol]
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


def get_first_ref(_inst):
	conectors = _inst.MEPModel.ConnectorManager.Connectors
	if not conectors:
		return None

	for con in conectors:
		con_neibor = [i for i in con.AllRefs]
		if con_neibor:
			return con_neibor[0].Owner
	return None


global doc
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView

reload = IN[1]  # type: ignore
outlist = list()

cab_fitting_cat = BuiltInCategory.OST_CableTrayFitting
param_name = "Raceway Service"
param_id = 79571


cab_fittings = inst_by_cat_strparamvalue(cab_fitting_cat, param_id, "", False)
neighbors = [get_first_ref(i) for i in cab_fittings]
result_list = zip(cab_fittings, neighbors)
ouitlist = [i[0] for i in result_list if not(i[1])]

# get parameter values
result_params = [[i[0], get_parval(i[1], param_name)]
	for i in result_list if i[1]]

outlist.extend(
	[i[0] for i in result_params if not(i[1])]
)

# set parameters
# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

map(lambda x:
	setup_param_value(x[0], param_name, x[1]), result_params)

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = outlist
