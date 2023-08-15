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


class DaliSys():
	def __init__(self, el_sys):
		self.rvt_sys = el_sys
		self.doc = el_sys.Document
		self.lights
		self.switches

# def get_sys_elements(_el_sys):
# 	# type: (Autodesk.Revit.DB.Electrical.ElectricalSystem) -> list

# 	"""Get count of all elements of the system including subsystems\n
# 		args:
# 			_el_sys - electrical system
# 			all_elements - list of elements (used for recursion)

# 		return:
# 			list() - system, count of elements
# 	"""
# 	doc = _el_sys.Document
# 	# get main elements
# 	sys_board_name = str(_el_sys.PanelName)
# 	sys_nummer = str(_el_sys.CircuitNumber)
# 	sys_name_string = sys_board_name + ": " + sys_nummer
# 	sys_elements = [i for i in _el_sys.Elements]

# 	# find all systems with the main panel as quasy panel

# 	testParam = BuiltInParameter.RBS_ELEC_CIRCUIT_PANEL_PARAM
# 	pvp = ParameterValueProvider(ElementId(int(testParam)))
# 	fnrvStr = FilterStringEquals()
# 	filter = ElementParameterFilter(
# 		FilterStringRule(pvp, fnrvStr, sys_name_string))

# 	sub_systems = FilteredElementCollector(doc).\
# 		OfCategory(BuiltInCategory.OST_ElectricalCircuit).\
# 		WherePasses(filter).\
# 		ToElements()

# 	# for all the systems get elemets list
# 	if sub_systems:
# 		for system in sub_systems:
# 			elems = system.Elements
# 			if elems:
# 				for elem in elems:
# 					sys_elements.append(elem)

# 	# from element list filter out quasy panels
# 	sys_elements = [i for i in sys_elements if i.Name != sys_name_string]
# 	return _el_sys, len(sys_elements)


# def get_DALI_info(_el_board):
# 	# type: (Autodesk.Revit.DB.FamilyInstance) -> list

# 	outlist = list()

# 	# filter out electrical circuit only
# 	circuits = toolsrvt.elsys_by_brd(_el_board)[1]
# 	elems_in_circuits = [int(i.LookupParameter("E_Light_number").AsString()) for i in circuits]

# 	current_switch = 1
# 	total_fixtures = 0
# 	terminal_occupied = 0
# 	for elems in elems_in_circuits:
# 		# not possible situation
# 		# it is possible to connect max 64 lightings to 1 switchgear
# 		check = all([total_fixtures + elems <= 64, terminal_occupied < 4])
# 		if elems > 64:
# 			outlist.append("ERR")

# 		# we are Ok with terminals and lightings
# 		elif check:
# 			total_fixtures += elems
# 			terminal_occupied += 1
# 			outlist.append("DALI_" + str(current_switch))

# 		# no free terminals or more than 64 lights
# 		# use next switch
# 		else:
# 			current_switch += 1
# 			total_fixtures = elems
# 			terminal_occupied = 1
# 			outlist.append("DALI_" + str(current_switch))

# 	return zip(circuits, outlist)
