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
	allsys = _brd.MEPModel.GetElectricalSystems()
	lowsys = _brd.MEPModel.GetAssignedElectricalSystems()
	
	# filter out non Power circuits
	allsys = [i for i in allsys
		if i.SystemType == Electrical.ElectricalSystemType.PowerCircuit]
	lowsys = [i for i in lowsys
		if i.SystemType == Electrical.ElectricalSystemType.PowerCircuit]

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
	main_circ_num = brd_main_circuit.CircuitNumber
	main_board = board_inst.Name

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
			main_circ_num = next_system.CircuitNumber
			main_board = current_board.Name
			break

	# convert circuit number to int
	regexp = re.compile(r"^\D*(\d+)")
	check = regexp.match(main_circ_num)
	main_circ_num = check.group(1)
	main_circ_num = int(main_circ_num)

	# convert circuit number to USV name
	if main_circ_num % 20 == 0:
		n_subsection = main_circ_num // 20
	else:
		n_subsection = main_circ_num // 20 + 1

	n_element = main_circ_num - (n_subsection - 1) * 20

	name = main_board + ":" + str(n_subsection) + "." + str(n_element)
	board_inst.get_Parameter(BuiltInParameter.RBS_ELEC_PANEL_NAME).Set(name)
	return name


doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application

reload = IN[1]  # type: ignore
calc_by_panel = IN[2]  # type: ignore

fnrvStr = FilterStringEquals()
pvp = ParameterValueProvider(ElementId(int(BuiltInParameter.ELEM_FAMILY_PARAM)))
frule = FilterStringRule(pvp, fnrvStr, "QUASI_Connector", False)
filter = ElementParameterFilter(frule)

# =================== part 1 of the script
# get quai_boards and change their parameters
quasi_boards = FilteredElementCollector(doc).\
	OfCategory(BuiltInCategory.OST_ElectricalEquipment).\
	WhereElementIsNotElementType().\
	WherePasses(filter).\
	ToElements()

elem_status = CheckoutStatus.OwnedByOtherUser
quasi_boards = [
	i for i in quasi_boards
	if WorksharingUtils.GetCheckoutStatus(doc, i.Id) != elem_status and
	any([
		"CP1-KE3W2C05" in i.Name,  # Emergency lighting panel hard coded
		"CP1-KE3L2B05" in i.Name  # Emergency lighting panel hard coded
	])]

# # =================== part 2 of the script
# # renumerate lighting fixtures in panel
# if calc_by_panel:
# 	# get all circuits of the panel
# 	em_board = UnwrapElement(IN[3])  # type: ignore
# 	circuits = elsys_by_brd(em_board)[1]
# else:
# 	# get only current circuit of the element
# 	# means, that only 1 circuit (connector) in faliy possible
# 	el_fixture = UnwrapElement(IN[3])  # type: ignore
# 	circuits = el_fixture.MEPModel.GetElectricalSystems()
# 	if circuits:
# 		circuits = [i for i in el_fixture.MEPModel.GetElectricalSystems()]

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# =================== part 3 of the script
# Set parameters for all quasi_boards
# it does not matter, if calc_by_panel.
# All quasi panels, that are avaliable, will be updated.
brd_updated = map(update_subboard_name, quasi_boards)

# # =================== part 4 of the script
# # Set parameters to lighting fixtures
# outlist = list()
# for circuit in circuits:
# 	# TODO check if circuit is electrical
# 	elems_in_circuit = searchInDeep(circuit, [])
# 	outlist.append(elems_in_circuit)
# 	if elems_in_circuit:
# 		for i, elem in enumerate(elems_in_circuit):
# 			outlist.append([elem, "E_Light_number", str(i + 1)])
# 			setup_param_value(elem, "E_Light_number", str(i + 1))

TransactionManager.Instance.TransactionTaskDone()
# =========End transaction

# OUT = circuits
OUT = brd_updated
