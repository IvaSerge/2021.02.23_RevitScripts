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


def get_sys_elements(_el_sys):
	# get main elements
	sys_elements = [i for i in _el_sys.Elements]

	# find if there any electrical board in the system
	# if the element is board and it's name == upperpanel.circuit numer
	# pop it out of the list
	# get all the systems of the board
	# for every system in the board get elements
	return sys_elements


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
app = uiapp.Application


reload = IN[1]  # type: ignore
calc_all = IN[2]  # type: ignore
outlist = list()

# only 1 element to calculate
if not calc_all:
	circuits_to_calculate = get_sys_by_selection()
	sys_elements = get_sys_elements(circuits_to_calculate[0])

# get all electrical systems that are modifiable
if calc_all:
	pass

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)


# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = sys_elements
