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
import importlib
import toolsrvt
importlib.reload(toolsrvt)


def get_sys_elements(_el_sys):
	# type: (Autodesk.Revit.DB.Electrical.ElectricalSystem) -> list

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
	sys_elements = [i for i in _el_sys.Elements]

	# find all systems with the main panel as quasy panel

	testParam = BuiltInParameter.RBS_ELEC_CIRCUIT_PANEL_PARAM
	pvp = ParameterValueProvider(ElementId(int(testParam)))
	fnrvStr = FilterStringEquals()
	filter = ElementParameterFilter(
		FilterStringRule(pvp, fnrvStr, sys_name_string))

	sub_systems = FilteredElementCollector(doc).\
		OfCategory(BuiltInCategory.OST_ElectricalCircuit).\
		WherePasses(filter).\
		ToElements()

	# for all the systems get elemets list
	if sub_systems:
		for system in sub_systems:
			elems = system.Elements
			if elems:
				for elem in elems:
					sys_elements.append(elem)

	# from element list filter out quasy panels
	sys_elements = [i for i in sys_elements if i.Name != sys_name_string]
	return _el_sys, len(sys_elements)


def get_first_circuit_number(_circuit):
	# type: (Autodesk.Revit.DB.Autodesk.Revit.DB.Electrical.ElectricalSystem) -> int
	"""Used for circuit sorting"""
	circuit_number_str = _circuit.Name
	regexp = re.compile(r"^F*(\d+)")
	check = regexp.match(circuit_number_str)
	return int(check.group(1))


def get_DALI_info(_el_board):
	# type: (Autodesk.Revit.DB.FamilyInstance) -> list

	outlist = list()

	# filter out electrical circuit only
	circuits = toolsrvt.elsys_by_brd(_el_board)[1]
	elems_in_circuits = [int(i.LookupParameter("E_Light_number").AsString()) for i in circuits]

	current_switch = 1
	total_fixtures = 0
	terminal_occupied = 0
	for elems in elems_in_circuits:
		# not possible situation
		# it is possible to connect max 64 lightings to 1 switchgear
		check = all([total_fixtures + elems <= 64, terminal_occupied < 4])
		if elems > 64:
			outlist.append("ERR")

		# we are Ok with terminals and lightings
		elif check:
			total_fixtures += elems
			terminal_occupied += 1
			outlist.append("DALI_" + str(current_switch))

		# no free terminals or more than 64 lights
		# use next switch
		else:
			current_switch += 1
			total_fixtures = elems
			terminal_occupied = 1
			outlist.append("DALI_" + str(current_switch))

	return zip(circuits, outlist)


def write_info(info_list, par_name):
	# # write parameter to circuit
	for i in info_list:
		elem = i[0]
		value = str(i[1])
		toolsrvt.setup_param_value(elem, par_name, value)


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
app = uiapp.Application

reload = IN[1]  # type: ignore
calc_all = IN[2]  # type: ignore
info_list = list()
boards_list = list()


# only 1 element to calculate
if not calc_all:
	# # get selected object
	# sel = uidoc.Selection.PickObject(  # type: ignore
	# 	Autodesk.Revit.UI.Selection.ObjectType.Element, "")
	# sel_obj = doc.GetElement(sel.ElementId)  # type: ignore
	# # TODO: Add here check of selection
	# boards_list.append(sel_obj)
	boards_list.append(UnwrapElement(IN[3]))  # type: ignore


# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# for board in board_list:
board = boards_list[0]
circuits_to_calculate = toolsrvt.elsys_by_brd(board)[1]

if circuits_to_calculate:
	for circuit in circuits_to_calculate:
		info = get_sys_elements(circuit)
		info_list.append(info)

write_info(info_list, "E_Light_number")
doc.Regenerate()

info_DALIL = get_DALI_info(board)
write_info(info_DALIL, "Switching Unit")

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

# OUT = info_list
OUT = get_DALI_info(board)
