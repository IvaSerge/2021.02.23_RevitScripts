"""modue to represent electrical panel as node of graph"""
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

dir_path = IN[0].DirectoryName  # type: ignore
sys.path.append(dir_path)


# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *


class el_panel:
	def __init__(self, _rvt_panel):
		# type: (Autodesk.Revit.DB.Electrical.ElectricalEquipment) -> any
		"""
		Extended electrical panel class
		"""
		self.rvt_panel = _rvt_panel  # type: Autodesk.Revit.DB.Electrical.ElectricalEquipment
		self.index_row: int
		self.index_column: int
		self.circuits_to_check: list[Autodesk.Revit.DB.Electrical.ElectricalSystem]
