"""modue to represent electrical panel as node of graph"""
import clr

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

# ================ local imports
import toolsrvt


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

	@staticmethod
	def panels_by_start_panel(_rvt_panel):
		# type: (Autodesk.Revit.DB.Electrical.ElectricalEquipment) -> list[el_panel]
		"""Get list of dependend panels. Important to set correct index of each panel

		args:\\
		_rvt_panel - start panel of the tree

		return:\\
		list of extended panel objects
		"""
		outlist = list()
		total_panels: int
		panels_to_check = list()

		start_elem = el_panel(_rvt_panel)
		start_elem.index_row, start_elem.index_column = 0, 0

		panels_to_check.append(start_elem)
		outlist.append(start_elem)

		while panels_to_check:
			panels_to_check.pop()

		return start_elem
