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

# ================ Local imports


def get_sys_by_selection():
	"""
	Get system by selected object
	"""
	el_sys_list = list()
	# # get system by selected object
	# sel = uidoc.Selection.PickObject(  # type: ignore
	# 	Autodesk.Revit.UI.Selection.ObjectType.Element, "")
	# sel_obj = doc.GetElement(sel.ElementId)  # type: ignore
	global IN
	sel_obj = UnwrapElement(IN[3])  # type: ignore

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


def setup_param_value(elem, name, pValue):
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


def get_sys_elements(_el_sys, all_elements=list()):
	# type: (Autodesk.Revit.DB.Electrical.ElectricalSystem, list()) -> list

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
	sys_elements = _el_sys.Elements

	# find if there any electrical board in the system
	for elem in sys_elements:
		# if the element is board and it's name == upperpanel.circuit numer
		# OST_ElectricalEquipment.Id == -2001040
		if elem.Category.Id == ElementId(-2001040):
			board_name = elem.Name
			# the board is quasi sub-board of the system
			if board_name == sys_name_string:
				# get subsystems of the board
				low_systems = elsys_by_brd(elem)[1]
				if low_systems:
					for low_sys in low_systems:
						get_sys_elements(low_sys, all_elements)
		else:
			all_elements.append(elem)
	elem_count = len(all_elements)
	return _el_sys, elem_count


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

for circuit in circuits_to_calculate:
	info = get_sys_elements(circuit, [])
	info_list.append(info)

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)


# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = info_list
