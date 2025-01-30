import clr
import os
import sys

# ================ Revit imports
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# ================ Python imports
from importlib import reload
from abc import ABC, abstractmethod
from System import Array
from System.Collections.Generic import *
import pandas as pd

# ================ local imports
import toolsrvt


class RvtPanel():
	"""
	Class represents and extends electrical panel
	"""

	def __init__(self, _rvt_instance):
		self.rvt_panel = _rvt_instance
		self.rvt_circuits = toolsrvt.elsys_by_brd(self.rvt_panel)[1]
	
	def get_circuts_info(self):
		outlist = list()
		if self.rvt_circuits is None:
			return None

		for circiut in self.rvt_circuits:
			# fist - get info about current circuti
			circuit_info = RvtPanel.get_circuit_info(circiut)
			if not circuit_info:
				continue
			outlist.append(circuit_info)

			# get info from next panel
			next_panel_info = RvtPanel.get_next_info(circiut)
			if next_panel_info:
				outlist.append(next_panel_info)

		return outlist


	@staticmethod
	def get_circuit_info(circuit):
		# Check if it is a circuit for a panel
		is_feeder = RvtPanel.check_circuit_is_feeder(circuit)

		# if circuit is nof a feeder - it will be passed
		if not is_feeder:
			return None
	
		# get info for current circuit
		circuit_number = circuit.CircuitNumber
		circuit_name = circuit.LoadName

		return [circuit_number, circuit_name]

	@staticmethod
	def check_circuit_is_feeder(circuit):
		# not a spare
		is_power_sys = circuit.SystemType == Electrical.ElectricalSystemType.PowerCircuit
		is_circuit_type = circuit.CircuitType == Electrical.CircuitType.Circuit
		if not is_power_sys or not is_circuit_type:
			return False

		# not single
		elems = list(circuit.Elements)
		if len(elems) > 1:
			return False

		# first element is panel
		first_elem:FamilyInstance = elems[0]
		if first_elem.Category.Id.IntegerValue != -2001040:
			return False

		# first element not quasi
		type_name = first_elem.Symbol.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString().lower()

		if "quasi" in type_name:
			return False

		return True

	@staticmethod
	def get_next_info(circuit):
		elems = list(circuit.Elements)
		rvt_next_panel:FamilyInstance = elems[0]
		next_panel:RvtPanel = RvtPanel(rvt_next_panel)
		next_panel_info = next_panel.get_circuts_info()
		return next_panel_info
