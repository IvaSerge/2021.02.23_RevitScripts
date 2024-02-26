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
import time
import datetime

import el_exceptions
from el_exceptions import test_exceptions

import importlib

# ================ local imports
import toolsrvt
importlib.reload(toolsrvt)


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


def GetEstimatedValues(_elSys, _testboard):
	# type: (Electrical.ElectricalSystem, FamilyInstance) -> list[Electrical.ElectricalSystem]
	"""Get Estimated values from elecrtical board for the circuit

		args:
			_elSys: system to be calculated
			_testboard: temporary board for manipulations

		return:
			param List[str] - list of installed values
	"""

	params_to_set = [
		"E_DemandFactor",
		"Demand Factor",
		"E_TotalInstalledLoad",
		"E_TotalEstLoad",
		"E_EstCurrent",
	]

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
			total_est_load, UnitTypeId.VoltAmperes)  # type: ignore
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
		current_estimated = round(UnitUtils.ConvertFromInternalUnits(rvt_current,
			UnitTypeId.Amperes) * 10) / 10  # type: ignore

	circuits = [_elSys] * len(params_to_set)
	values = [
		rvt_DemandFactor,
		rvt_DemandFactor,
		rvt_TotalInstalledLoad,
		total_est_load,
		current_estimated]

	return zip(circuits, params_to_set, values)


def SetEstimatedValues(values):
	elem = values[0]
	param = values[1]
	value = values[2]
	toolsrvt.setup_param_value(elem, param, value)


# ================ GLOBAL VARIABLES
start_time = time.time()
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
	FilterStringRule(pvp, fnrvStr, DISTR_SYS_NAME))

voltage_230 = UnitUtils.ConvertToInternalUnits(230, UnitTypeId.Volts)  # type: ignore
voltage_400 = UnitUtils.ConvertToInternalUnits(400, UnitTypeId.Volts)  # type: ignore

distrSys = FilteredElementCollector(doc).\
	OfCategory(BuiltInCategory.OST_ElecDistributionSys).\
	WhereElementIsElementType().\
	WherePasses(filter).\
	ToElements()[0].Id

if not calculate_all:
	# get all assigned circuits in the panel
	panel_assigned_circuits = toolsrvt.elsys_by_brd(panel_instance)

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

	circuits_to_calculate = [
		i for i in circuits_to_calculate
		if all([
			i.SystemType == Electrical.ElectricalSystemType.PowerCircuit,
			any([i.Voltage == voltage_230, i.Voltage == voltage_400]),
			i.BaseEquipment,
			WorksharingUtils.GetCheckoutStatus(doc, i.Id) != CheckoutStatus.OwnedByOtherUser
		])]


# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# try:
TESTBOARD = doc.Create.NewFamilyInstance(
	XYZ(0, 0, 0), testBoardType, Structure.StructuralType.NonStructural)
TESTBOARD.get_Parameter(
	BuiltInParameter.RBS_FAMILY_CONTENT_DISTRIBUTION_SYSTEM).Set(distrSys)

values = list()

for circuit in circuits_to_calculate:
	# get values
	circuit_values = GetEstimatedValues(circuit, TESTBOARD)
	if circuit_values:
		values.extend(circuit_values)

for value in values:
	SetEstimatedValues(value)

doc.Delete(TESTBOARD.Id)

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

end_time = time.time()
total_time_seconds = end_time - start_time
total_time = datetime.datetime.utcfromtimestamp(total_time_seconds).strftime("%H:%M:%S.%f")
time_str = (f"Total execution time: {total_time[:-3]}")
OUT = values, time_str
