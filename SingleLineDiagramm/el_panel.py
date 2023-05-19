"""modue to represent electrical panel as node of graph"""
import clr

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

# ================ local imports
import toolsrvt


def panels_by_start_panel(_rvt_panel):
		# type: (Autodesk.Revit.DB.Electrical.ElectricalEquipment) -> list[el_panel]
		"""Get list of dependend panels. Important to set correct index of each panel

		args:\\
		_rvt_panel - start panel of the tree

		return:\\
		list of extended panel objects
		"""
		outlist = list()
		total_panels = 1
		panels_to_check = list()

		start_elem = el_panel(_rvt_panel)
		start_elem.index_row, start_elem.index_column = total_panels, 0

		panels_to_check.append(start_elem)
		outlist.append(start_elem)

		while panels_to_check:
			# for i in range(3):
			current_panel: el_panel = panels_to_check[-1]
			next_panel = current_panel.find_upper_panel()

			if next_panel:
				next_panel_obj = el_panel(next_panel)
				next_panel_obj.index_column = current_panel.index_column + 1
				total_panels += 1
				next_panel_obj.index_row = total_panels
				panels_to_check.append(next_panel_obj)
				outlist.append(next_panel_obj)
			else:
				# current panel do not contain upper panels.
				panels_to_check.pop()

		return outlist


class el_panel:

	def __init__(self, _rvt_panel):
		# type: (Autodesk.Revit.DB.Electrical.ElectricalEquipment) -> any
		"""
		Extended electrical panel class
		"""
		self.rvt_panel = _rvt_panel  # type: Autodesk.Revit.DB.Electrical.ElectricalEquipment
		self.index_row: int
		self.index_column: int
		self.circuits_to_check = toolsrvt.elsys_by_brd(_rvt_panel)[1]

	def find_upper_panel(self):
		# type: (el_panel) -> Autodesk.Revit.DB.Electrical.ElectricalEquipment
		"""
		find the first upper panel
		"""

		# no circuits - no panels
		if not self.circuits_to_check:
			return None

		while self.circuits_to_check:
			current_circuit = self.circuits_to_check.pop(0)

			# check if there is a panel in the circuit and return it
			circuit_elements = [i for i in current_circuit.Elements]
			if len(circuit_elements) == 1 and circuit_elements[0].Category.Id == ElementId(-2001040):
				if "Quasi" not in circuit_elements[0].Symbol.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString():
					return circuit_elements[0]
		return None
