
from re import X
from this import d
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

clr.AddReferenceByName('Microsoft.Office.Interop.Excel, Version=11.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c')
from Microsoft.Office.Interop import Excel  # type: ignore

import System
from System import Array
from System.Collections.Generic import *

System.Threading.Thread.CurrentThread.CurrentCulture = System.Globalization.CultureInfo("en-US")
from System.Runtime.InteropServices import Marshal

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# ================ python imports
from operator import itemgetter
import re


def getByCatAndStrParam(_bic, _bip, _val, _isType):
	global doc
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


def mm_to_ft(mm):
	return 3.2808 * mm / 1000


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


def circuit_number_to_usv_link(_main_circ_num):
	# type: (str) -> str
	"""Convert Revit circuit number to realistic link to the panel

	args:
		main_circ_num - revit circuit number
	return:
		value_str - converterd number
	"""
	main_circ_num = str(_main_circ_num)

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

	value_str = str(n_subsection) + "." + str(n_element)

	return value_str


global doc
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView


board_inst = UnwrapElement(IN[3])  # type: ignore

# select view for diagramm
view_name = IN[2]  # type: ignore
view_diagramm = getByCatAndStrParam(
	BuiltInCategory.OST_Views,
	BuiltInParameter.VIEW_NAME,
	view_name,
	False)[0]

# type to install
type_first = getByCatAndStrParam(
	BuiltInCategory.OST_DetailComponents,
	BuiltInParameter.SYMBOL_NAME_PARAM,
	"2D_diagramm_NOT_1P",
	True)[0]

type_emergency = getByCatAndStrParam(
	BuiltInCategory.OST_DetailComponents,
	BuiltInParameter.SYMBOL_NAME_PARAM,
	"2D_diagramm_E01",
	True)[0]

type_exit = getByCatAndStrParam(
	BuiltInCategory.OST_DetailComponents,
	BuiltInParameter.SYMBOL_NAME_PARAM,
	"2D_diagramm_Exit",
	True)[0]


# for circuit in boards:
circuits = [i for i in elsys_by_brd(board_inst)[1]
	if i.CircuitType == Autodesk.Revit.DB.Electrical.CircuitType.Circuit]


circuits.sort(key=lambda x: x.StartSlot)

circuits_info_list = list()
for circuit_inst in circuits:

	circuit_num = circuit_inst.CircuitNumber
	circuit_usv_link = circuit_number_to_usv_link(circuit_num)

	circuit_str = board_inst.Name + ":" + circuit_usv_link
	circuit_name = circuit_inst.LoadName
	circuit_wire_size = circuit_inst.WireSizeString
	circuit_wire_type = circuit_inst.WireType.Name

	if "#2.5" in circuit_wire_size and "NYM" in circuit_wire_type:
		circuit_wire_str = "NYM 3x2.5"
	elif "#2.5" in circuit_wire_size and "NHXH E30" in circuit_wire_type:
		circuit_wire_str = "NHXH E30 3x2.5"
	elif "4" in circuit_wire_size and "NYM" in circuit_wire_type:
		circuit_wire_str = "NYM 3x4"
	elif "4" in circuit_wire_size and "NHXH E30" in circuit_wire_type:
		circuit_wire_str = "NHXH E30 3x4"
	else:
		circuit_wire_str = ""

	# find all elements by "Panel" and "Circuit Number"
	elems_in_circuit = getByCatAndStrParam(
		BuiltInCategory.OST_LightingFixtures,
		BuiltInParameter.RBS_ELEC_CIRCUIT_PANEL_PARAM,
		circuit_str,
		False)

	if not(elems_in_circuit):
		continue

	# read element parameters
	params_to_set = list()
	for elem in elems_in_circuit:
		elem_mark = get_parval(elem.Symbol, "WINDOW_TYPE_ID")  # Revit parameter "Type Mark"
		elem_light_num = get_parval(elem, "E_Light_number")
		param_list = list()
		param_list.append(elem_mark)
		param_list.append(circuit_usv_link)
		param_list.append(int(elem_light_num))
		param_list.append(circuit_name)
		param_list.append(circuit_wire_str)
		params_to_set.append(param_list)

	params_to_set.sort(key=itemgetter(2))
	circuits_info_list.append(params_to_set)


# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

instances_on_view = list()
for pnt_y, params_to_set in enumerate(circuits_info_list):

	# insert 2D on drawing, add parameters
	# insert first element
	# Start point
	instance_on_view = None

	if params_to_set:
		insert_pnt = XYZ(0, -(pnt_y + 1) * mm_to_ft(2000), 0)
		instance_on_view = doc.Create.NewFamilyInstance(
			insert_pnt,
			type_first,
			view_diagramm)
		instance_on_view.LookupParameter("Beschriftung 1").Set(params_to_set[0][3])
		instance_on_view.LookupParameter("Beschriftung 2").Set(params_to_set[0][4])
		instances_on_view.append(instance_on_view)

	for pnt_x, info in enumerate(params_to_set):
		insert_pnt = XYZ((pnt_x + 2) * mm_to_ft(1000), -(pnt_y + 1) * mm_to_ft(2000), 0)

		if any(["03" in info[0], "04" in info[0], "06" in info[0]]):
			symbol_type = type_exit
		else:
			symbol_type = type_emergency

		instance_on_view = doc.Create.NewFamilyInstance(
			insert_pnt,
			symbol_type,
			view_diagramm)

		# set parameters to new instance
		setup_param_value(instance_on_view, "Type Mark", info[0])
		setup_param_value(instance_on_view, "Panel", info[1])
		setup_param_value(instance_on_view, "E_Light_number", str(info[2]))

		instances_on_view.append(instance_on_view)

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = circuits_info_list
