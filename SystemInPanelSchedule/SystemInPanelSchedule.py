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


def inst_by_cat_strparamvalue(_bic, _bip, _val, _isType):
	"""Get all family instances by category and parameter value

		args:
		_bic: BuiltInCategory.OST_xxx
		_bip: BuiltInParameter

		return:
		list()[Autodesk.Revit.DB.FamilySymbol]
	"""
	if _isType:
		fnrvStr = FilterStringEquals()
		pvp = ParameterValueProvider(ElementId(int(_bip)))
		frule = FilterStringRule(pvp, fnrvStr, _val, False)
		filter = ElementParameterFilter(frule)
		elem = FilteredElementCollector(doc).\
			OfCategory(_bic).\
			WhereElementIsElementType().\
			WherePasses(filter).\
			ToElements()
	else:
		fnrvStr = FilterStringEquals()
		pvp = ParameterValueProvider(ElementId(int(_bip)))
		frule = FilterStringRule(pvp, fnrvStr, _val, False)
		filter = ElementParameterFilter(frule)
		elem = FilteredElementCollector(doc).\
			OfCategory(_bic).\
			WhereElementIsNotElementType().\
			WherePasses(filter).\
			ToElements()
	return elem


def get_bip(paramName):
	builtInParams = System.Enum.GetValues(BuiltInParameter)
	param = []
	for i in builtInParams:
		if i.ToString() == paramName:
			param.append(i)
			return i


def category_by_bic_name(_bicString):
	global doc
	bicList = System.Enum.GetValues(BuiltInCategory)
	bic = [i for i in bicList if _bicString == i.ToString()][0]
	return Category.GetCategory(doc, bic)


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


# ================ GLOBAL VARIABLES
uiapp = DocumentManager.Instance.CurrentUIApplication
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
app = uiapp.Application
DISTR_SYS_NAME = "230/400V"

global doc  # type: ignore
doc = DocumentManager.Instance.CurrentDBDocument


reload = IN[1]  # type: ignore[reportUndefinedVariable]
panel_name = IN[2]  # type: ignore

outlist = list()
error_list = list()

all_views = FilteredElementCollector(doc).\
	OfClass(Autodesk.Revit.DB.Electrical.PanelScheduleView).\
	WhereElementIsNotElementType()


shedule = [x for x in all_views
	if doc.GetElement(x.GetPanel()).Name == panel_name][0]  # type: Electrical.PanelScheduleView

panel_name_bip = get_bip("RBS_ELEC_PANEL_NAME")
panel_instance = inst_by_cat_strparamvalue(BuiltInCategory.OST_ElectricalEquipment, panel_name_bip, panel_name, False)

# check if Panel name is unique
if len(panel_instance) > 1:
	raise ValueError("More than 1 board with the same name in model")
else:
	panel_instance = panel_instance[0]  # type: FamilyInstance


# get all assigned circuits in the panel
panel_assigned_circuits = elsys_by_brd(panel_instance)

# check if there is any circuit in the Panel
if len(panel_assigned_circuits[1]) == 0:
	raise ValueError("No circuits found")
else:
	panel_assigned_circuits = panel_assigned_circuits[1]


# get info about all cells in the shadule
# shedule_circuits_found = list()
# while len(shedule_circuits_found) != len(panel_assigned_circuits):
# for i in range(5):
# circuit_in_shedule = shedule.GetCircuitByCell(3, 2)
# shedule_circuits_found.append(circuit_in_shedule)


# circuit = view_in_work.GetCircuitByCell(2, 4)

# for each circuit in the panel
	# find circuit current position
	# disconnect circuit
	# connect to the virtual panel
	# get electrical parameters
	# write circuit parameters
	# connect circuit back
	# move to the correct position

# after work with circuits
# change cell infos "as it was"


# slots_list = shedule.IsSpare(1, 2)
# slot_texts = shedule.GetCircuitByCell(2, 2)
# OUT = circuit_in_shedule, get_parval(circuit_in_shedule, "RBS_ELEC_CIRCUIT_NUMBER")
circuit_in_shedule = shedule.GetCircuitByCell(5, 1)

OUT = circuit_in_shedule, panel_assigned_circuits
