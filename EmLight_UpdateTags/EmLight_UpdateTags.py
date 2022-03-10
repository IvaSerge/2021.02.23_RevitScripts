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


# ================ local imports
import EmLight_SearchInSys
from EmLight_SearchInSys import *


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


def update_subboard_name(board_inst):
	"""
	Board type "QUASI_Connector" symbol is subboard.
	Board name need to be changed according to current circuit name
	"""
	# TODO: do not understand, what do not work here

	brd_main_circuit = elsys_by_brd(board_inst)[0]

	if not brd_main_circuit:
		return None

	current_board = board_inst
	main_board = board_inst.Name
	main_circ_num = brd_main_circuit.CircuitNumber

	while True:
		if current_board:
			board_is_quasi = current_board.Symbol.Family.Name == "QUASI_Connector"
		else:
			return "None"

		if board_is_quasi:
			# get upper board
			try:
				next_system = elsys_by_brd(current_board)[0]
				next_board = next_system.BaseEquipment
				current_board = next_board
			except:
				break
		else:
			main_board = current_board.Name
			main_circ_num = next_system.CircuitNumber
			break

	name = main_board + ": " + main_circ_num
	board_inst.get_Parameter(BuiltInParameter.RBS_ELEC_PANEL_NAME).Set(name)

	return name


doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application

reload = IN[1]  # type: ignore
calc_all = IN[2]  # type: ignore

fnrvStr = FilterStringEquals()
pvp = ParameterValueProvider(ElementId(int(BuiltInParameter.ELEM_FAMILY_PARAM)))
frule = FilterStringRule(pvp, fnrvStr, "QUASI_Connector", False)
filter = ElementParameterFilter(frule)

quasi_boards = FilteredElementCollector(doc).\
	OfCategory(BuiltInCategory.OST_ElectricalEquipment).\
	WhereElementIsNotElementType().\
	WherePasses(filter).\
	ToElements()

elem_status = CheckoutStatus.OwnedByOtherUser
quasi_boards = [i for i in quasi_boards
	if WorksharingUtils.GetCheckoutStatus(doc, i.Id) != elem_status]

fnrvStr = FilterStringEquals()
pvp = ParameterValueProvider(ElementId(int(BuiltInParameter.ELEM_FAMILY_PARAM)))
frule = FilterStringRule(pvp, fnrvStr, "QUASI_Connector", False)
filter = ElementParameterFilter(frule)

em_board = UnwrapElement(IN[3])  # type: ignore
circuits = elsys_by_brd(em_board)[1]


# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

brd_updated = map(update_subboard_name, quasi_boards)

outlist = list()
for circuit in circuits:
	# TODO check if circuit is electrical
	elems_in_circuit = searchInDeep(circuit, [])
	outlist.append(elems_in_circuit)
	if elems_in_circuit:
		for i, elem in enumerate(elems_in_circuit):
			outlist.append([elem, "E_Light_number", str(i + 1)])
			setup_param_value(elem, "E_Light_number", str(i + 1))

TransactionManager.Instance.TransactionTaskDone()
# =========End transaction

OUT = quasi_boards