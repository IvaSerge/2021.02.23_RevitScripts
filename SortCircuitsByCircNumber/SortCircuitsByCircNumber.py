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


def elsys_by_brd(_brd):
	"""Get all systems of electrical board.
		args:
		_brd - electrical board FamilyInstance
		return list(1, 2) where:
		1 - main electrical circuit
		2 - list of connectet low circuits
	"""
	allsys = _brd.MEPModel.GetElectricalSystems()
	lowsys = _brd.MEPModel.GetAssignedElectricalSystems()
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


def get_estimated_load(_elSys, _testboard):
	"""Get estimated load of circuit by connecting it to temporar board"""
	global doc
	calcSystem = _elSys

	# Main board of electrical system
	mainBoard = calcSystem.BaseEquipment

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

	convert_TotalEstLoad = UnitUtils.ConvertFromInternalUnits(
		rvt_TotalEstLoad, DisplayUnitType.DUT_VOLT_AMPERES)

	# reconnect circuit back
	calcSystem.SelectPanel(mainBoard)
	doc.Regenerate()

	return convert_TotalEstLoad, rvt_DemandFactor


# ================ GLOBAL VARIABLES
global doc  # type: ignore
doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
app = uiapp.Application
DISTR_SYS_NAME = "230/400V"

reload = IN[1]  # type: ignore
panel_instance = UnwrapElement(IN[2])  # type: ignore

# Take the type the same as selected board
testBoardType = UnwrapElement(IN[3]).Symbol  # type: ignore

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


# get all assigned circuits in the panel
panel_assigned_circuits = elsys_by_brd(panel_instance)

# check if there is any circuit in the Panel
if len(panel_assigned_circuits[1]) == 0:
	raise ValueError("No circuits found")
else:
	circuits_to_calculate = panel_assigned_circuits[1]


circ_trip = [get_parval(x, "Trip") for x in circuits_to_calculate]
circ_poles = [x.PolesNumber for x in circuits_to_calculate]

circ_list = [
	x for x in zip(circuits_to_calculate, circ_trip, circ_poles)]

circ_list.sort(key=lambda x: (x[1], x[2]), reverse=True)
circ_list = [i[0] for i in circ_list]


# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

TESTBOARD = doc.Create.NewFamilyInstance(
	XYZ(0, 0, 0), testBoardType, Structure.StructuralType.NonStructural)
TESTBOARD.get_Parameter(
	BuiltInParameter.RBS_FAMILY_CONTENT_DISTRIBUTION_SYSTEM).Set(distrSys)

for circ in circ_list:
	circ.SelectPanel(TESTBOARD)
	doc.Regenerate()

for circ in circ_list:
	circ.SelectPanel(panel_instance)
	doc.Regenerate()

doc.Delete(TESTBOARD.Id)

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = circ_list
