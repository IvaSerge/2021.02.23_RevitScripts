import clr
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

import System


def GetBuiltInParam(paramName):
	builtInParams = System.Enum.GetValues(BuiltInParameter)
	param = []
	for i in builtInParams:
		if i.ToString() == paramName:
			param.append(i)
			return i


def GetParVal(elem, name):
	value = " "
	# Параметр пользовательский
	param = elem.LookupParameter(name)
	# параметр не найден. Надо проверить, есть ли такой же встроенный параметр
	if not(param):
		param = elem.get_Parameter(GetBuiltInParam(name))
	# Если параметр найден, считываем значение
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


def SetupParVal(elem, name, pValue):
	global doc
	# Параметр пользовательский
	param = elem.LookupParameter(name)
	# параметр не найден. Надо проверить, есть ли такой же встроенный параметр
	if not(param):
		param = elem.get_Parameter(GetBuiltInParam(name))
	if param:
		param.Set(pValue)
	return elem


def getSwitchedInst(_switchSys):
	outlist = list(), list()
	for sys in _switchSys:
		switch = sys.BaseEquipment
		if switch:
			outlist[0].append(switch.Id)
			outlist[1].append(sys)
		elems = sys.Elements
		for elem in elems:
			outlist[0].append(elem.Id)
			outlist[1].append(sys)
	return outlist


def getSystems(_brd):
	"""Get all systems of electrical board.

		args:
		_brd - electrical board FamilyInstance

		return:
		list(1, 2) where:
		1 - feeder
		2 - list of branch systems
	"""
	try:
		board_all_systems = [i for i in _brd.MEPModel.ElectricalSystems]
	except TypeError:
		# raise TypeError("Board \"%s\" have no systems" % brd_name)
		return None, None
	try:
		board_branch_systems = [i for i in _brd.MEPModel.AssignedElectricalSystems]
		board_branch_systems.sort(
			key=lambda x:
			float(GetParVal(x, "RBS_ELEC_CIRCUIT_NUMBER")))
	except TypeError:
		# raise ValueError("Board \"%s\" have no branch systems" % brd_name)
		return board_all_systems[0], None
	if len(board_branch_systems) == len(board_all_systems):
		# raise ValueError("Board \"%s\" have no feeder" % brd_name)
		return None, board_branch_systems

	branch_systems_id = [i.Id for i in board_branch_systems]
	board_feeder = [
		i for i in board_all_systems
		if i.Id not in branch_systems_id][0]
	return board_feeder, board_branch_systems


def readInfo(_elem):
	"""
	Read electrical parameters of element

	args:
		_elem[0] - FamilyInstance
		_elem[1] - Type of electrical system

	return:
		_elem - FamilyInstance
		list() - list of circuit indexes

	index structure is XYY where:
	X: - board prefix, YY: - circuit number with leading zeros
	"""
	global doc
	elem = _elem[0]
	elem_cat_Id = elem.Category.Id
	brd_cat_Id = Category.GetCategory(
		doc, BuiltInCategory.OST_ElectricalEquipment).Id
	sysType = _elem[1]

	# Element is Electrical board:
	if elem_cat_Id == brd_cat_Id:
		brd_systems = getSystems(elem)
		mainciruit = brd_systems[0]
		# no feeder found
		if not(mainciruit):
			return elem, None

		# check if it is correct type of the system
		check_circ_type = mainciruit.SystemType == sysType
		if not(check_circ_type):
			return elem, None

		# After all make index
		circPanel = mainciruit.BaseEquipment
		# check if electrical system is connected to any board
		try:
			# is connected
			circPanelName = circPanel.get_Parameter(
				BuiltInParameter.RBS_ELEC_CIRCUIT_PREFIX).AsString()
			circNumber = str(mainciruit.CircuitNumber)
			fnumber = '{:02}'.format(int(float(circNumber)))
			circInfo = circPanelName + fnumber
			return elem, [circInfo]
		except:
			# Not connected
			return elem, ["NotConnected"]

	# For all other elements
	allCircuits = elem.MEPModel.ElectricalSystems

	# element is not connectes
	if not(allCircuits):
		return elem, None

	outlist = list()
	for circuit in allCircuits:
		# check if it is correct type of the system
		check_circ_type = circuit.SystemType == sysType
		if not(check_circ_type):
			continue

		try:
			# check if electrical system is connected to any board
			circPanel = circuit.BaseEquipment
			circPanelName = circPanel.get_Parameter(
				BuiltInParameter.RBS_ELEC_CIRCUIT_PREFIX).AsString()
			circNumber = str(circuit.CircuitNumber)
			fnumber = '{:02}'.format(int(float(circNumber)))
			circInfo = circPanelName + fnumber
			outlist.append(circInfo)
		except:
			outlist.append("NotConnected")

	outlist.sort(key=lambda x: (x[1], x[0]))
	return elem, outlist


def writeInfo(_info):
	elem = _info[0][0]
	circuitsInfo = _info[0][1]
	ParamsList = _info[1]
	# Check if there any parameter to set
	# If there is no parameter - set white space
	if not(circuitsInfo):
		circuitsInfo = [" "] * len(ParamsList)

	# Check if there are all parameters in the list
	paramCount = len(ParamsList) - len(circuitsInfo)
	if paramCount > 0:
		for i in range(paramCount):
			circuitsInfo.append(" ")

	# Set values
	map(lambda x: SetupParVal(elem, x[0], x[1]), zip(
		ParamsList, circuitsInfo))
	return elem, circuitsInfo, ParamsList


def getSwitchNumber(_elem):
	global switchedInstances
	if _elem.Id in switchedInstances[0]:
		elemIndex = switchedInstances[0].index(_elem.Id)
		switchSys = switchedInstances[1][elemIndex]
		sysNumber = GetParVal(switchSys, "MC Object Variable 2")
		return _elem, [sysNumber]
	else:
		return _elem, [" "]


doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application

switchSystems = FilteredElementCollector(doc)\
	.OfCategory(BuiltInCategory.OST_SwitchSystem)\
	.OfClass(MEPSystem)

switchedInstances = getSwitchedInst(switchSystems)

dataElem = FilteredElementCollector(doc)\
	.OfCategory(BuiltInCategory.OST_DataDevices)\
	.WhereElementIsNotElementType()\
	.ToElements()

electroElem = FilteredElementCollector(doc)\
	.OfCategory(BuiltInCategory.OST_ElectricalFixtures)\
	.WhereElementIsNotElementType()\
	.ToElements()

leuchten = FilteredElementCollector(doc)\
	.OfCategory(BuiltInCategory.OST_LightingFixtures)\
	.WhereElementIsNotElementType()\
	.ToElements()

lichtschalter = FilteredElementCollector(doc)\
	.OfCategory(BuiltInCategory.OST_LightingDevices)\
	.WhereElementIsNotElementType()\
	.ToElements()

electroBoards = FilteredElementCollector(doc)\
	.OfCategory(BuiltInCategory.OST_ElectricalEquipment)\
	.WhereElementIsNotElementType()\
	.ToElements()

NotRuf = FilteredElementCollector(doc)\
	.OfCategory(BuiltInCategory.OST_NurseCallDevices)\
	.WhereElementIsNotElementType()\
	.ToElements()

reload = IN[0]

ParamsELT = [
	"Beschriftung 1",
	"Beschriftung 2"]

ParamsDAT = [
	"Beschriftung 3",
	"Beschriftung 4",
	"Beschriftung 5",
	"Beschriftung 6"]

ParamsSwitch = ["MC Object Variable 2"]

elemList = list()
# elemList = [UnwrapElement(IN[1])]
map(elemList.append, dataElem)
map(elemList.append, electroElem)
map(elemList.append, leuchten)
map(elemList.append, lichtschalter)
map(elemList.append, electroBoards)
# map(elemList.append, NotRuf)

eltInfo = map(
	readInfo, zip(elemList, [Electrical.ElectricalSystemType.PowerCircuit] * len(elemList)))

# datInfo = map(
# 	readInfo, zip(elemList, [
# 		Electrical.ElectricalSystemType.Data] * len(elemList)))

# switchInfo = map(getSwitchNumber, elemList)

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

eltParamInfo = map(writeInfo, zip(eltInfo, [ParamsELT] * len(eltInfo)))
# datParamInfo = map(writeInfo, zip(datInfo, [ParamsDAT] * len(datInfo)))
# switchParamInfo = map(writeInfo, zip(switchInfo, [ParamsSwitch]*len(switchInfo)))

TransactionManager.Instance.TransactionTaskDone()
# =========End transaction

# OUT = zip(elemList, [Electrical.ElectricalSystemType.PowerCircuit] * len(elemList))
OUT = eltParamInfo
