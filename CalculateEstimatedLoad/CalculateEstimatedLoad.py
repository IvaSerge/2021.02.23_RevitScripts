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
import math
from math import sqrt

import el_exceptions
from el_exceptions import test_exceptions


def GetBuiltInParam(paramName):
	builtInParams = System.Enum.GetValues(BuiltInParameter)
	param = []
	for i in builtInParams:
		if i.ToString() == paramName:
			param.append(i)
			return i


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
		lowsys.sort(key=lambda x: get_parval(x, "RBS_ELEC_CIRCUIT_NUMBER"))
		return mainboardsys, lowsys
	else:
		return [i for i in allsys][0], None


def get_bip(paramName):
	# type: (str) -> BuiltInParameter
	builtInParams = System.Enum.GetValues(BuiltInParameter)
	param = []
	for i in builtInParams:
		if i.ToString() == paramName:
			param.append(i)
			return i


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


def get_circuit_row(_el_sys):
	global doc

	# Main board of electrical system
	mainBoard = _el_sys.BaseEquipment

	# find the shedule of electrical board
	board_schedule = [x for x in FilteredElementCollector(doc).
		OfClass(Autodesk.Revit.DB.Electrical.PanelScheduleView).
		ToElements()
		if x.TargetId == mainBoard.Id]  # type: Autodesk.Revit.DB.Electrical.PanelScheduleView

	if board_schedule:
		# find the row of the circuit in schedule
		board_schedule = board_schedule[0]  # type: Autodesk.Revit.DB.Electrical.PanelScheduleView
		max_cells = board_schedule.GetTableData().NumberOfSlots
		board_circuits = [
			board_schedule.GetCircuitIdByCell(i, 1).IntegerValue
			for i in range(1, max_cells + 1)]
		try:
			board_row = board_circuits.index(_el_sys.Id.IntegerValue)
		except:
			board_row = [None, None]
	else:
		board_row = [None, None]

	return board_row, board_schedule


def get_estimated_load(_elSys, _testboard):
	"""Get estimated load of circuit by connecting it to temporar board"""
	global doc
	calcSystem = _elSys

	# perform changes in subtransaction
	with SubTransaction(doc) as sub_tr:
		sub_tr.Start()

		# reconnect system from Main to Test board
		calcSystem.SelectPanel(_testboard)
		doc.Regenerate()

		# Get parameters from test board
		rvt_DemandFactor = _testboard.get_Parameter(
			BuiltInParameter.
			RBS_ELEC_PANEL_TOTAL_DEMAND_FACTOR_PARAM).AsDouble()

		rvt_TotalEstLoad = _testboard.get_Parameter(
			BuiltInParameter.
			RBS_ELEC_PANEL_TOTALESTLOAD_PARAM).AsDouble()

		sub_tr.RollBack()

	return rvt_TotalEstLoad, rvt_DemandFactor  # convert_TotalEstLoad, rvt_DemandFactor


def SetEstimatedValues(_elSys, _testboard):
	# type: (Electrical.ElectricalSystem, FamilyInstance) -> list[Electrical.ElectricalSystem]
	"""Copy Estimated values from elecrtical board to the circuit

	args:
		_elSys: system to be calculated
		_testboard: temporary board for manipulations

	return:
		param List[str] - list of installed values

	"""

	# If circuit owned by other - return None
	elem_stat = Autodesk.Revit.DB.WorksharingUtils.GetCheckoutStatus(
		doc, _elSys.Id)
	if elem_stat == Autodesk.Revit.DB.CheckoutStatus.OwnedByOtherUser:
		return None

	# check if it is a real circuit
	# it it is spare or space - no actions requiered
	circ_type = _elSys.CircuitType
	calcSystem = _elSys
	rvt_TotalInstalledLoad = _elSys.ApparentLoad
	if circ_type != Electrical.CircuitType.Circuit:
		return None

	if test_exceptions(_elSys):
		calc_parameters = get_estimated_load(_elSys, _testboard)
		total_est_load = calc_parameters[0]
		convert_TotalEstLoad = UnitUtils.ConvertFromInternalUnits(
			total_est_load, DisplayUnitType.DUT_VOLT_AMPERES)
		rvt_DemandFactor = round(calc_parameters[1], 2)
		# calculate parameters
		poles_number = calcSystem.PolesNumber
		if poles_number == 1:
			current_estimated = round(
				(convert_TotalEstLoad / 230) * 10) / 10
		else:
			current_estimated = round((convert_TotalEstLoad / (400 * sqrt(3))) * 10) / 10
	else:
		# if not an exception - demand factor == 1
		rvt_DemandFactor = 1
		total_est_load = rvt_TotalInstalledLoad
		rvt_current = _elSys.ApparentCurrent
		current_estimated = round(UnitUtils.ConvertFromInternalUnits(
			rvt_current, DisplayUnitType.DUT_AMPERES) * 10) / 10

	# Write parameters in Circuit
	calcSystem.LookupParameter("E_DemandFactor").Set(rvt_DemandFactor)
	calcSystem.LookupParameter("Demand Factor").Set(rvt_DemandFactor)
	calcSystem.LookupParameter("E_TotalInstalledLoad").Set(rvt_TotalInstalledLoad)
	calcSystem.LookupParameter("E_TotalEstLoad").Set(total_est_load)
	calcSystem.LookupParameter("E_EstCurrent").Set(current_estimated)
	return rvt_DemandFactor, total_est_load, current_estimated


# ================ GLOBAL VARIABLES
global doc  # type: ignore
doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
app = uiapp.Application
DISTR_SYS_NAME = "230/400V"

reload = IN[1]  # type: ignore
calculate_all = IN[3]  # type: ignore
panel_instance = UnwrapElement(IN[2])  # type: ignore
outlist = list()

# Take the type the same as selected board
testBoardType = UnwrapElement(IN[4]).Symbol  # type: ignore

# find and set distribution system
testParam = BuiltInParameter.SYMBOL_NAME_PARAM
pvp = ParameterValueProvider(ElementId(int(testParam)))
fnrvStr = FilterStringEquals()
filter = ElementParameterFilter(
	FilterStringRule(pvp, fnrvStr, DISTR_SYS_NAME, False))

distrSys = FilteredElementCollector(doc).\
	OfCategory(BuiltInCategory.OST_ElecDistributionSys).\
	WhereElementIsElementType().\
	WherePasses(filter).\
	ToElements()[0].Id

if not(calculate_all):
	# get all assigned circuits in the panel
	panel_assigned_circuits = elsys_by_brd(panel_instance)

	# check if there is any circuit in the Panel
	if len(panel_assigned_circuits[1]) == 0:
		raise ValueError("No circuits found")
	else:
		circuits_to_calculate = panel_assigned_circuits[1]
else:
	# get all circuits in the model
	# Get all electrical circuits
	# Circuit type need to be electrilca only
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
		230, DisplayUnitType.DUT_VOLTS)
	voltage_400 = UnitUtils.ConvertToInternalUnits(
		400, DisplayUnitType.DUT_VOLTS)

	circuits_to_calculate = [
		i for i in circuits_to_calculate
		if i.Voltage == voltage_230 or i.Voltage == voltage_400
	]

	# filter out not owned circuits
	circuits_to_calculate = [
		i for i in circuits_to_calculate
		if WorksharingUtils.GetCheckoutStatus(doc, i.Id) != CheckoutStatus.OwnedByOtherUser
	]

	# Filtering out not connected circuits
	circuits_to_calculate = [i for i in circuits_to_calculate if i.BaseEquipment]

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

TESTBOARD = doc.Create.NewFamilyInstance(
	XYZ(0, 0, 0), testBoardType, Structure.StructuralType.NonStructural)
TESTBOARD.get_Parameter(
	BuiltInParameter.RBS_FAMILY_CONTENT_DISTRIBUTION_SYSTEM).Set(distrSys)

param_info = [SetEstimatedValues(x, TESTBOARD) for x in circuits_to_calculate]

doc.Delete(TESTBOARD.Id)

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

# OUT = param_info
OUT = param_info
