# ================ system imports
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
sys.path.append(IN[0].DirectoryName)  # type: ignore

import System
from System import Array
from System.Collections.Generic import *

# ================ Revit imports
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# ================ Python imports
import re
from operator import itemgetter

# ================ Local imports


def get_sys_by_selection():
	"""
	Get system by selected object
	"""
	el_sys_list = list()
	# get system by selected object
	sel = uidoc.Selection.PickObject(  # type: ignore
		Autodesk.Revit.UI.Selection.ObjectType.Element, "")
	sel_obj = doc.GetElement(sel.ElementId)  # type: ignore

	# check if selection is electrical board
	# OST_ElectricalEquipment.Id == -2001040
	if sel_obj.Category.Id == ElementId(-2001040):
		sys_el = sel_obj.MEPModel.ElectricalSystems
		sys_all = [x.Id for x in sel_obj.MEPModel.AssignedElectricalSystems]
		el_sys_list = [x for x in sys_el if x.Id not in sys_all]
		# filter out electrical circuit only
		el_sys_list = [
			x for x in el_sys_list
			if x.SystemType == Electrical.ElectricalSystemType.PowerCircuit]
	else:
		el_sys_list = [x for x in sel_obj.MEPModel.ElectricalSystems]
	return el_sys_list


def get_circuit_number(_circuit_number_str):
	# type: (Autodesk.Revit.DB.Autodesk.Revit.DB.Electrical.ElectricalSystem) -> int
	"""Used for circuit sorting"""
	regexp = re.compile(r"^[A-Za-z]*(\d+)")
	check = regexp.match(_circuit_number_str)
	return int(check.group(1))


def get_param_values(elem, params):
	return [get_parval(elem, i) for i in params]


def get_parval(elem, name):
	# type: (FamilyInstance, str) -> any
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


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
app = uiapp.Application

reload = IN[1]  # type: ignore
calc_all = IN[2]  # type: ignore
info_list = list()

# only 1 element to calculate
if not calc_all:
	circuits_to_calculate = get_sys_by_selection()

# get all electrical systems
if calc_all:
	# get all circuits in the model
	# electrical circuit type ID == 6
	testParam = BuiltInParameter.RBS_ELEC_CIRCUIT_TYPE
	pvp = ParameterValueProvider(ElementId(int(testParam)))
	sysRule = FilterIntegerRule(pvp, FilterNumericEquals(), 6)
	filter = ElementParameterFilter(sysRule)

	circuits_to_calculate = FilteredElementCollector(doc).\
		OfCategory(BuiltInCategory.OST_ElectricalCircuit).\
		WhereElementIsNotElementType().WherePasses(filter).\
		ToElements()

	voltage_230 = UnitUtils.ConvertToInternalUnits(
		230, UnitTypeId.VoltAmperes)
	voltage_400 = UnitUtils.ConvertToInternalUnits(
		400, UnitTypeId.VoltAmperes)

	circuits_to_calculate = [
		i for i in circuits_to_calculate
		if i.Voltage == voltage_230 or i.Voltage == voltage_400
	]

	# Filtering circuits for requiered panels only
	filtered_circuits = list()
	for i in circuits_to_calculate:
		base_panel = i.BaseEquipment
		if not base_panel:
			continue
		model_name = base_panel.Symbol.get_Parameter(BuiltInParameter.ALL_MODEL_MODEL).AsString()
		if not model_name:
			continue
		filter_model_name = any([
			"2A" in model_name,
			"2C" in model_name,
			"2K" in model_name,
		])

		if filter_model_name:
			filtered_circuits.append(i)

# read circuit parameters
params = [
	"Panel",
	"Circuit Number",
	"Trip",
	"Frame",
	"_Breaker_Type"]


param_val_list = [get_param_values(i, params) for i in filtered_circuits]
sort_key = lambda x: (x[0], get_circuit_number(x[1]))
param_val_list.sort(key=sort_key)

param_val_list.insert(0, params)

OUT = param_val_list
