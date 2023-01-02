
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

import itertools
from itertools import chain


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
		frule = FilterStringRule(pvp, fnrvStr, _val)
		filter = ElementParameterFilter(frule)
		elem = FilteredElementCollector(doc).\
			OfCategory(_bic).\
			WhereElementIsElementType().\
			WherePasses(filter).\
			ToElements()
	else:
		fnrvStr = FilterStringEquals()
		pvp = ParameterValueProvider(ElementId(int(_bip)))
		frule = FilterStringRule(pvp, fnrvStr, _val)
		filter = ElementParameterFilter(frule)
		elem = FilteredElementCollector(doc).\
			OfCategory(_bic).\
			WhereElementIsNotElementType().\
			WherePasses(filter).\
			ToElements()
	return elem


def get_first_ref(_inst):
	# type: (FamilyInstance) -> FamilyInstance
	conectors = _inst.MEPModel.ConnectorManager.Connectors
	if not conectors:
		return None

	for con in conectors:
		con_neibor = [i for i in con.AllRefs]
		if con_neibor:
			return con_neibor[0].Owner
	return None


def get_parameter_list(_elements, _parameters):
	"""Get pair: element_to_set - parameter value

		args:
		_elements[0]: Family instance for setting parameters
		_elements[0]: Family instance for getting parameters
		_parameters: List of parameter names to get-set

		return: [element, param_name, param_value]
	"""

	element_to_set = _elements[0]
	element_to_read = _elements[1]
	values_list = list()
	for param in _parameters:
		param_value = get_parval(element_to_read, param)
		values_list.append([element_to_set, param, param_value])
	return values_list


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
PARAM_NAMES = [
	"Raceway Service",
	"Cable Tray ID",
	"TSLA_SCOPE_ID",
	"Tool Prio",
	"Phase Created",
	"Tool Scope ID"]


cab_fittings = inst_by_cat_strparamvalue(cab_fitting_cat, param_id, "", False)
neighbors = [get_first_ref(i) for i in cab_fittings]
neighbor_pairs = zip(cab_fittings, neighbors)

# that's error need to be clarified
without_neighbor = [i[0] for i in neighbor_pairs if not i[1]]

# filter pairs only with neighbor
neighbor_pairs = [i for i in neighbor_pairs if i[1]]

# filter out instances witch naghbor have empty "Raceway Service"
instances_raceway_empty = [i[0] for i in neighbor_pairs if not get_parval(i[1], "Raceway Service")]

pairs_with_raceway = [i for i in neighbor_pairs if get_parval(i[1], "Raceway Service")]

# read parameters
pairs_to_set = [get_parameter_list(i, PARAM_NAMES) for i in pairs_with_raceway]
pairs_to_set = list(itertools.chain.from_iterable(pairs_to_set))


# set parameters
# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

func_set_param = lambda x: setup_param_value(x[0], x[1], x[2])
map(func_set_param, pairs_to_set)

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = without_neighbor, instances_raceway_empty
