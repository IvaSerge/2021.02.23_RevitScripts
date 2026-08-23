import re
import clr

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

import toolsrvt


class ElecSys:
	"""Handler for a Revit electrical system.

	Reads system data, processes it, then writes results back to Revit.

	Class variables:
		overwright: whether to overwrite an existing description.
			If False, an existing description is left unchanged.
			A value is written only when the description is missing
			and the parameter is empty.
	"""

	overwright: bool = False

	def __init__(self, elec_system: Electrical.ElectricalSystem):
		# main Revit electrical system
		self.rvt_sys: Electrical.ElectricalSystem = elec_system
		self.wire_string = str()
		self.cable_description = str()
		self._get_wire_string()

	def _get_wire_string(self) -> None:
		# only real circuits have a wire size
		isNotCircuit = self.rvt_sys.CircuitType != Autodesk.Revit.DB.Electrical.CircuitType.Circuit
		isNotPower = self.rvt_sys.SystemType != Autodesk.Revit.DB.Electrical.ElectricalSystemType.PowerCircuit
		if any([isNotCircuit, isNotPower]):
			self.wire_string = None
			return

		# WireSizeString can fail if wire is not assigned
		try:
			cable_cross_section = self.rvt_sys.WireSizeString
		except:
			self.wire_string = "Failed"
			return
		cable_type = toolsrvt.get_parval(self.rvt_sys.WireType, "ALL_MODEL_TYPE_NAME")

		# Cable type need to be cleaned. 
		# Spaces " ", "_" to be removed
		cleaned_cable_type = cable_type.strip()
		cleaned_cable_type = cable_type.strip(".")
		cleaned_cable_type = cleaned_cable_type.strip("_")

		# update wire size. If wire type is NYCWY or NAYCWY or other type from the list
		reduced_PE_types = ["NYCWY", "NAYCWY"]
		reduce_to = {
			"25": "16",
			"35": "16",
			"50": "25",
			"70": "35",
			"95": "50",
			"120": "70",
			"150": "70",
		}

		# if cable type is not in the list
		cable_section_updated = cable_cross_section

		# if cable type is in the list - PE wire need to be reduced
		# See possible wire size examples
		# 2 runs of 3-#120, 1-#120 mm, 1-#120
		# 2 runs of 3-#120, 1-#70
		# 3-#70, 1-#70 mm, 1-#35
		# Using re it is necessary:
		# 1. find the 1st combination of digits like (1-#??) or (3-#??)
		# 2. Get the ??? value and find replacement in reduce_to list
		# 3. find the last combination like (1-#???) and replace it to (1-#???) - new reduced value
		if any(pe_type in cleaned_cable_type for pe_type in reduced_PE_types):
			first_match = re.search(r"\d+-#(\d+)", cable_cross_section)
			if first_match:
				reduced_size = reduce_to.get(first_match.group(1))
				if reduced_size:
					pe_matches = list(re.finditer(r"1-#\d+", cable_cross_section))
					if pe_matches:
						last_pe = pe_matches[-1]
						cable_section_updated = (
							cable_cross_section[:last_pe.start()]
							+ "1-#" + reduced_size
							+ cable_cross_section[last_pe.end():]
						)

		cable_section_updated = cable_section_updated.rstrip(" mm")

		self.wire_string = cleaned_cable_type + " " + cable_section_updated
