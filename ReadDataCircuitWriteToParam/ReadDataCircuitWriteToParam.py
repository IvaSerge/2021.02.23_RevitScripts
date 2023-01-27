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
		if i.CircuitType == Electrical.CircuitType.Circuit]
	lowsys = [i for i in lowsys
		if i.CircuitType == Electrical.CircuitType.Circuit]

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


def update_subboard_name(board_inst):
	"""
	Board type "QUASI_Connector" symbol is subboard.
	Board name need to be changed according to current circuit name
	"""
	brd_main_circuit = elsys_by_brd(board_inst)[0]
	if not brd_main_circuit:
		return None

	current_board = board_inst

	while True:
		if not current_board:
			return None

		board_is_quasi = current_board.Symbol.Family.Name == "QUASI_Connector"

		if board_is_quasi:
			# get upper board
			next_system = elsys_by_brd(current_board)[0]
			next_board = next_system.BaseEquipment
			current_board = next_board
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

fnrvStr = FilterStringEquals()
pvp = ParameterValueProvider(ElementId(int(BuiltInParameter.ELEM_FAMILY_PARAM)))
frule = FilterStringRule(pvp, fnrvStr, "QUASI_Connector")
filter = ElementParameterFilter(frule)

electroBoards = FilteredElementCollector(doc).\
	OfCategory(BuiltInCategory.OST_ElectricalEquipment).\
	WhereElementIsNotElementType().\
	WherePasses(filter).\
	ToElements()

reload = IN[1]  # type: ignore
calc_all = IN[2]  # type: ignore

if calc_all:
	elemList = electroBoards

if not calc_all:
	elemList = [UnwrapElement(IN[3])]  # type: ignore

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

brd_updated = map(update_subboard_name, elemList)

TransactionManager.Instance.TransactionTaskDone()
# =========End transaction

# OUT = brd_updated
OUT = elemList
