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
import importlib
from importlib import reload

# ================ Local imports
import calc_overall_vd
reload(calc_overall_vd)
from calc_overall_vd import *


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
		brd_systems = elsys_by_brd(sel_obj)
		if brd_systems[0]:
			el_sys_list.append(brd_systems[0])
		if brd_systems[1]:
			circuits_to_calculate = [circuit for circuit in brd_systems[1]
				if circuit.CircuitType == Autodesk.Revit.DB.Electrical.CircuitType.Circuit]
			el_sys_list.extend(circuits_to_calculate)
		el_sys_list = [
			x for x in el_sys_list
			if x.SystemType == Electrical.ElectricalSystemType.PowerCircuit]
	else:
		el_sys_list = [x for x in sel_obj.MEPModel.GetElectricalSystems()]

	# Filter out not electrical circuti
	filtered_circuits = []
	for circuit in el_sys_list:
		c_type = circuit.CircuitType == Autodesk.Revit.DB.Electrical.CircuitType.Circuit
		c_sys_type = circuit.SystemType == Autodesk.Revit.DB.Electrical.ElectricalSystemType.PowerCircuit
		c_check = all([c_type, c_sys_type])
		if c_check:
			filtered_circuits.append(circuit)

	return filtered_circuits


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
		lowsys.sort(key=lambda x: x.StartSlot)
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
	builtInParams = [i for i in System.Enum.GetNames(BuiltInParameter)]
	param = None
	for i, i_name in enumerate(builtInParams):
		if i_name == paramName:
			param = System.Enum.GetValues(BuiltInParameter)[i]
			break
	return param


def get_el_sys(_elem):
	elem_cat = _elem.Category.Id.IntegerValue
	# check if it is electrical board
	if elem_cat == -2001040:
		el_sys = elsys_by_brd(_elem)[0]
	else:
		sys_type = Autodesk.Revit.DB.Electrical.ElectricalSystemType.PowerCircuit
		el_sys = _elem.MEPModel.GetElectricalSystems()
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
	FilterStringRule(pvp, fnrvStr, DISTR_SYS_NAME))

distrSys = FilteredElementCollector(doc).\
	OfCategory(BuiltInCategory.OST_ElecDistributionSys).\
	WhereElementIsElementType().\
	WherePasses(filter).\
	ToElements()[0].Id

reload = IN[1]  # type: ignore
calc_all = IN[2]  # type: ignore
outlist = list()

# only 1 element to calculate
if not calc_all:
	circuits_to_calculate = get_sys_by_selection()

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

	voltage_230 = UnitUtils.ConvertToInternalUnits(230, UnitTypeId.Volts)  # type: ignore
	voltage_400 = UnitUtils.ConvertToInternalUnits(400, UnitTypeId.Volts)  # type: ignore

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

if not circuits_to_calculate:
	raise ValueError("No electrical system found")

vd_list = [get_vd(circuit) for circuit in circuits_to_calculate]

for i in vd_list:
	el_sys = i[0]
	# skiped not owned system
	if WorksharingUtils.GetCheckoutStatus(doc, el_sys.Id) == CheckoutStatus.OwnedByOtherUser:
		continue

	el_vd = str(round(i[1][0] * 100) / 100)
	el_vd_overall = str(round(sum(i[1]) * 100) / 100)
	el_sys.LookupParameter("CP_Voltage Drop").Set(el_vd)
	el_sys.LookupParameter("CP_Voltage Drop Overall").Set(el_vd_overall)

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = vd_list
# OUT = circuits_to_calculate
