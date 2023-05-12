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


def elsys_by_brd(_brd):
	# type: (FamilyInstance) -> list
	"""Get all systems of electrical board.

		args:
		_brd - electrical board FamilyInstance

		return list(1, 2) where:
		1 - main electrical circuit
		2 - list of connectet low circuits
	"""
	allsys = _brd.MEPModel.GetElectricalSystems()
	lowsys = _brd.MEPModel.GetAssignedElectricalSystems()

	# filter out non Power circuits
	allsys = [i for i in allsys
		if i.SystemType == Electrical.ElectricalSystemType.PowerCircuit]
	lowsys = [i for i in lowsys
		if i.SystemType == Electrical.ElectricalSystemType.PowerCircuit]

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
	if not param:
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
	# custom parameter
	param = elem.LookupParameter(name)
	# check is it a BuiltIn parameter if not found
	if not param:
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


def get_sys_elements(_el_sys):
	# type: (Autodesk.Revit.DB.Electrical.ElectricalSystem) -> list

	"""Get count of all elements of the system including subsystems\n
		args:
			_el_sys - electrical system
			all_elements - list of elements (used for recursion)

		return:
			list() - system, count of elements
	"""

	# get main elements
	sys_board_name = str(_el_sys.PanelName)
	sys_nummer = str(_el_sys.CircuitNumber)
	sys_name_string = sys_board_name + ": " + sys_nummer
	sys_elements = [i for i in _el_sys.Elements]

	# find all systems with the main panel as quasy panel

	testParam = BuiltInParameter.RBS_ELEC_CIRCUIT_PANEL_PARAM
	pvp = ParameterValueProvider(ElementId(int(testParam)))
	fnrvStr = FilterStringEquals()
	filter = ElementParameterFilter(
		FilterStringRule(pvp, fnrvStr, sys_name_string))

	sub_systems = FilteredElementCollector(doc).\
		OfCategory(BuiltInCategory.OST_ElectricalCircuit).\
		WherePasses(filter).\
		ToElements()

	# for all the systems get elemets list
	if sub_systems:
		for system in sub_systems:
			elems = system.Elements
			if elems:
				for elem in elems:
					sys_elements.append(elem)

	# from element list filter out quasy panels
	sys_elements = [i for i in sys_elements if i.Name != sys_name_string]
	return _el_sys, len(sys_elements)


def get_first_circuit_number(_circuit):
	# type: (Autodesk.Revit.DB.Autodesk.Revit.DB.Electrical.ElectricalSystem) -> int
	"""Used for circuit sorting"""
	circuit_number_str = _circuit.Name
	regexp = re.compile(r"^F*(\d+)")
	check = regexp.match(circuit_number_str)
	return int(check.group(1))


def write_DALI_info(_el_board):
	# type: (Autodesk.Revit.DB.FamilyInstance) -> list

	# filter out electrical circuit only
	circuits = elsys_by_brd(_el_board)[1]
	elems_in_circuits = [int(i.LookupParameter("E_Light_number").AsString()) for i in circuits]

	# # for every circuit get ammount of fixtures in circuit
	# total_fixtures = 0
	# current_switch = 1
	# for circuit in circuits:
	# 	fixtures_in_circuit = int(circuit.LookupParameter("E_Light_number").AsString())

	# 	# it is possible to connect 64 lightings to 1 switchgear
	# 	# 64 lightings can be connected, 0 in reserve
	# 	if fixtures_in_circuit + total_fixtures > 64:
	# 		# not possible to connect to the device
	# 		# switch to other device
	# 		total_fixtures = fixtures_in_circuit
	# 		current_switch += 1
	# 	else:
	# 		# possible to connect to the device
	# 		total_fixtures += fixtures_in_circuit

	# 	str_switch = "DALI_" + str(current_switch)
	# 	circuit.LookupParameter("Switching Unit").Set(str_switch)
	return elems_in_circuits


def write_circuit_info(info_list):
	# # write parameter to circuit
	par_name = "E_Light_number"
	for i in info_list:
		elem = i[0]
		value = str(i[1])
		setup_param_value(elem, par_name, value)


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
app = uiapp.Application

reload = IN[1]  # type: ignore
calc_all = IN[2]  # type: ignore
info_list = list()
boards_list = list()


# only 1 element to calculate
if not calc_all:
	# # get selected object
	# sel = uidoc.Selection.PickObject(  # type: ignore
	# 	Autodesk.Revit.UI.Selection.ObjectType.Element, "")
	# sel_obj = doc.GetElement(sel.ElementId)  # type: ignore
	# # TODO: Add here check of selection
	# boards_list.append(sel_obj)
	boards_list.append(UnwrapElement(IN[3]))


# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# for board in board_list:
board = boards_list[0]
circuits_to_calculate = elsys_by_brd(board)[1]

if circuits_to_calculate:
	for circuit in circuits_to_calculate:
		info = get_sys_elements(circuit)
		info_list.append(info)

# write_circuit_info(info_list)

# for board in boards_list:
# write_DALI_info(board)

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

# OUT = info_list
OUT = write_DALI_info(board)
