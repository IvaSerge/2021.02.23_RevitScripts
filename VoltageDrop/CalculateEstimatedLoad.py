# ================ system imports
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'

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


def get_est_current(_elSys, _testboard, _doc):
	# type: (Electrical.ElectricalSystem, FamilyInstance, Document) -> list[Electrical.ElectricalSystem]
	"""Copy Estimated values from elecrtical board to the circuit

	args:
		_elSys: system to be calculated
		_testboard: temporary board for manipulations

	return:
		param List[str] - list of installed values

	"""
	# check if it is a real circuit
	# it it is spare or space - no actions requiered
	circ_type = _elSys.CircuitType
	if circ_type != Electrical.CircuitType.Circuit:
		return None

	calcSystem = _elSys
	poles_number = calcSystem.PolesNumber

	# Main board of electrical system
	mainBoard = calcSystem.BaseEquipment

	# reconnect system from Main to Test board
	calcSystem.SelectPanel(_testboard)
	_doc.Regenerate()

	# Get parameters from test board
	# rvt_DemandFactor = _testboard.get_Parameter(
	# 	BuiltInParameter.
	# 	RBS_ELEC_PANEL_TOTAL_DEMAND_FACTOR_PARAM).AsDouble()

	rvt_TotalEstLoad = _testboard.get_Parameter(
		BuiltInParameter.
		RBS_ELEC_PANEL_TOTALESTLOAD_PARAM).AsDouble()

	convert_TotalEstLoad = UnitUtils.ConvertFromInternalUnits(
		rvt_TotalEstLoad, DisplayUnitType.DUT_VOLT_AMPERES)

	# calculate parameters
	if poles_number == 1:
		current_estimated = round(
			(convert_TotalEstLoad / 230) * 10) / 10
	else:
		current_estimated = round(
			(convert_TotalEstLoad / (400 * sqrt(3))) * 10) / 10

	# rvt_TotalInstalledLoad = _elSys.ApparentLoad

	# reconnect circuit back
	calcSystem.SelectPanel(mainBoard)
	_doc.Regenerate()
	return current_estimated
