# ================ system imports
import clr

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
		self.lights = list()
		self.switches = list()

	def get_low_systems(self):
		# type: (Autodesk.Revit.DB.Electrical.ElectricalSystem) -> list[Autodesk.Revit.DB.Electrical.ElectricalSystem]

		"""Get all low systems of the current system\n
		args:
			self - electrical system

		return:
			list() - dependent systems
		"""
		systems_checked = list()
		systems_found = list()
		systems_found.append(self.rvt_sys)
		while systems_found:
			el_sys = systems_found.pop()
			systems_checked.append(el_sys)
			for elem in el_sys.Elements:
				# check if it is electrical panel
				if elem.Category.Id == ElementId(-2001040):
					low_systems = toolsrvt.elsys_by_brd(elem)[1]
					if not low_systems:
						continue
					low_systems = [circuit for circuit in low_systems
						if circuit.CircuitType == Autodesk.Revit.DB.Electrical.CircuitType.Circuit]
					systems_found.extend(low_systems)
		return systems_checked

	def get_sys_elements(self):
		"""Get all elements including elements in low systems\n
		args:
			self - electrical system

		return:
			list() - elements list
		"""
		low_systems = self.get_low_systems()
		return low_systems

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
