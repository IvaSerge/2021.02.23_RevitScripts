import clr

# ================ Revit imports
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *


class ElecSys:
	"""Handler for a Revit electrical system.

	Reads system data, processes it, then writes results back to Revit.
	"""

	def __init__(self, elec_system: Electrical.ElectricalSystem):
		# main Revit electrical system
		self.rvt_sys: Electrical.ElectricalSystem = elec_system
		self.wire_string = str()
		self.cable_description = str()
		self._get_wire_string()

	def _get_wire_string(self) -> None:
		# only real circuits have a wire size
		if self.rvt_sys.CircuitType != Electrical.CircuitType.Circuit:
			return

		# WireSizeString can fail if wire is not assigned
		try:
			self.wire_string = self.rvt_sys.WireSizeString
		except:
			return
