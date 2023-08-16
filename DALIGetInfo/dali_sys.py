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
	params_to_set = list()

	def __init__(self, el_sys):
		self.rvt_sys = el_sys
		self.doc = el_sys.Document
		self.lights = list()
		self.switches = list()
		self.DALI_control = str()
		self.current_sum = str()
		DaliSys.get_sys_elements(self)

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
		elem_list = list()
		for el_sys in low_systems:
			elem_list.extend(el_sys.Elements)
		# filter by category
		self.lights = [i for i in elem_list if i.Category.Id == ElementId(-2001120)]
		self.switches = [i for i in elem_list if i.Category.Id == ElementId(-2008087)]

	@staticmethod
	def get_DALI_controls_info(dali_systems):
		current_switch = 1
		total_fixtures = 0
		terminal_occupied = 0
		for dali_sys in dali_systems:
			# not possible situation
			# it is possible to connect max 64 lightings to 1 DALI control unit
			elems = len(dali_sys.lights)
			check = all([total_fixtures + elems <= 64, terminal_occupied < 4])

			if elems > 64:
				dali_sys.DALI_control = "ERR"
				dali_sys.current_sum = elems

			# we are Ok with terminals and lightings
			elif check:
				total_fixtures += elems
				terminal_occupied += 1
				dali_sys.DALI_control = "DALI_" + str(current_switch)
				dali_sys.current_sum = total_fixtures

			# no free terminals or more than 64 lights
			# use next switch
			else:
				current_switch += 1
				total_fixtures = elems
				terminal_occupied = 1
				dali_sys.DALI_control = "DALI_" + str(current_switch)
				dali_sys.current_sum = total_fixtures

	def create_params_list(self):
		elem = self.rvt_sys
		DaliSys.params_to_set.append([elem, "E_Light_number", str(len(self.lights))])
		DaliSys.params_to_set.append([elem, "Switching Unit", str(len(self.switches))])
		if self.DALI_control:
			DaliSys.params_to_set.append([elem, "Control Unit", self.DALI_control])

	@classmethod
	def write_info(cls):
		for param_info in cls.params_to_set:
			toolsrvt.setup_param_value(
				param_info[0],
				param_info[1],
				param_info[2])
