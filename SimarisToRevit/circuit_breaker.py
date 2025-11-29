# circuit_breaker.py
# This module defines the CircuitBreaker class for modeling circuit breakers
# based on settings parsed from CSV data.

import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

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

# ================ Python imports
import re
import toolsrvt

class CircuitBreaker:
	"""
	A class representing a circuit breaker with settings from CSV data.
	
	This class is initialized with breaker settings (a frozenset of key-value pairs)
	and can be extended with methods for breaker-specific logic.
	"""

	doc = None

	@classmethod
	def _get_revit_element_by_description_(cls, description):
		# Parse via re the description string.
		# If string is not of correct format - raise value error

		doc = cls.doc
		re_circuit_number = re.compile(r"(?<=\[).*(?=\])")
		re_panel_name = re.compile(r".+(?=\[)")
		circuit_number_match = re_circuit_number.search(description)
		panel_name_match = re_panel_name.search(description)

		if not panel_name_match:
			raise ValueError(f"Invalid description format: Could not parse panel name from '{description}'")

		panel_name = panel_name_match.group(0).strip()

		if not circuit_number_match:
			raise ValueError(f"Invalid description format: Could not parse circuit number from '{description}'")

		circuit_number = circuit_number_match.group(0).strip()

		# Find the panel instance
		panel_rvt_list = toolsrvt.inst_by_cat_strparamvalue(
			doc,
			BuiltInCategory.OST_ElectricalEquipment,
			BuiltInParameter.RBS_ELEC_PANEL_NAME,
			panel_name,
			False)

		if not panel_rvt_list or len(panel_rvt_list) == 0:
			raise ValueError(f"Panel not found: '{panel_name}'")

		# Assume unique panel; take the first one
		panel_rvt = panel_rvt_list[0]

		# If circuit number is "0" - settings are for main panel
		if circuit_number == "0":
			return panel_rvt

		# It is a circuit breaker inside the panel. In Revit it is electrical circuit element
		try:
			# Assuming toolsrvt.elsys_by_brd returns [systems, circuits] or similar; [1] is circuits list
			circuits_rvt = toolsrvt.elsys_by_brd(panel_rvt)[1]
		except Exception as e:
			# Circuit in Revit not found. Panel is empty or error
			error_text = f"Panel does not have branch circuits: {panel_name} (Error: {str(e)})"
			raise ValueError(error_text)

		if not circuits_rvt:
			raise ValueError(f"No circuits found in panel: '{panel_name}'")

		# Find the specific circuit by circuit number
		for circuit in circuits_rvt:
			circuit_start_slot = circuit.StartSlot
			if int(circuit_start_slot) == int(circuit_number):
				return circuit

		# If no matching circuit found
		print(f"Circuit not found in panel {panel_name}[{circuit_number}]")
		raise ValueError(f"Circuit '{circuit_number}' not found in panel '{panel_name}'")



	def __init__(self, breaker_settings):
		"""
		Initializes the CircuitBreaker with the provided settings.
		
		:param breaker_settings: A frozenset of (key, value) tuples representing the breaker's parameters.
		"""
		# For now, this is a dummy implementation: store the settings as a dictionary
		settings = dict(breaker_settings)

		# Get the Revit element using the Designation from settings
		designation = settings.get("Designation")
		if not designation:
			raise ValueError("Missing 'Designation' in breaker settings")

		self.revit_element = CircuitBreaker._get_revit_element_by_description_(designation)

