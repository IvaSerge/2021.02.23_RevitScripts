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

# ================ Local imports
import circuit_voltage_drop
from circuit_voltage_drop import calc_circuit_vd
import calc_overall_vd
from calc_overall_vd import get_vd


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
	# board have upper and lower circuits
	if lowsys and allsys:
		lowsysId = [i.Id for i in lowsys]
		mainboardsysLst = [i for i in allsys if i.Id not in lowsysId]
		# board have no main circuit
		if len(mainboardsysLst) == 0:
			mainboardsys = None
		else:
			mainboardsys = mainboardsysLst[0]
		lowsys = [i for i in allsys if i.Id in lowsysId]
		lowsys.sort(key=lambda x: get_parval(x, "RBS_ELEC_CIRCUIT_NUMBER"))
		return mainboardsys, lowsys

	# board have no circuits
	if not allsys and not lowsys:
		return None, None

	# board have only main circuit
	if not lowsys:
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


def get_el_sys(_elem):
	elem_cat = _elem.Category.Id.IntegerValue
	# check if it is electrical board
	if elem_cat == -2001040:
		el_sys = elsys_by_brd(_elem)[0]
	else:
		sys_type = Autodesk.Revit.DB.Electrical.ElectricalSystemType.PowerCircuit
		el_sys = _elem.MEPModel.ElectricalSystems
		el_sys = [i for i in el_sys if i.SystemType == sys_type][0]
	return el_sys


# ================ GLOBAL VARIABLES
global doc  # type: ignore
doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
app = uiapp.Application
DISTR_SYS_NAME = "230/400V"

calc_overall_vd.doc = doc

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

reload = IN[1]  # type: ignore
calc_all = IN[2]  # type: ignore
el_instance = UnwrapElement(IN[3])  # type: ignore
outlist = list()

# only 1 element to calculate
if not calc_all:
	circuits_to_calculate = [get_el_sys(el_instance)]

# get all electrical systems that are modifiable
if calc_all:
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


# vd_list = [get_vd(circuit) for circuit in circuits_to_calculate]


# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)


# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = circuits_to_calculate
