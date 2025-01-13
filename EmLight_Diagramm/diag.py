"""
This module to represent 2D diagramm
"""


import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import System
from System import Array
from System.Collections.Generic import *

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

# ================ Dynamo imports
clr.AddReference('ProtoGeometry')
import Autodesk.DesignScript

from Autodesk.DesignScript.Geometry import *

clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
from Revit.Elements import *
clr.ImportExtensions(Revit.GeometryConversion)
clr.ImportExtensions(Revit.GeometryReferences)

# ================ Python imports
import importlib
from importlib import reload

# ================ local imports
import toolsrvt
reload(toolsrvt)


class Diagramm():

	doc = None
	view_diagramm = None
	type_first = None
	type_emergency = None
	type_exit = None
	start_point_x = 0
	start_point_y = 0

	def __init__(self, rvt_elem, column, row):
		self.insert_point = None
		self.params = list()
		self.rvt_elem = rvt_elem
		self.symbol_type = None
		self.symbol_instance = None
		self.row = row
		self.column = column
		self.get_elem_symbol()

	def calc_insert_point(self):
		pnt_x = self.start_point_x + self.column * toolsrvt.mm_to_ft(1000)
		pnt_y = self.start_point_y - self.row * toolsrvt.mm_to_ft(2000)
		pnt_z = 0
		insert_xyz = XYZ(pnt_x, pnt_y, pnt_z)
		self.insert_point = insert_xyz

	def create_elem_on_view(self):
		self.calc_insert_point()
		dia_inst = self.doc.Create.NewFamilyInstance(
			self.insert_point,
			self.symbol_type,
			self.view_diagramm)
		self.symbol_instance = dia_inst

	def set_parameters(self):
		if not self.params or not self.symbol_instance:
			return None
		for param_info in self.params:
			param_name = param_info[0]
			param_val = param_info[1]
			toolsrvt.setup_param_value(
				self.symbol_instance,
				param_name,
				param_val)
		return param_name, param_val

	def get_elem_symbol(self):
		elem_family_str = self.rvt_elem.Symbol.FamilyName
		exit_signs_types = ["E03", "E04", "E06"]
		if any(exit_type in elem_family_str for exit_type in exit_signs_types):
			self.symbol_type = self.type_exit
		else:
			self.symbol_type = self.type_emergency
		return self.symbol_type
	
	def get_params_to_set(self):
		elem_mark = toolsrvt.get_parval(
			self.rvt_elem.Symbol, "WINDOW_TYPE_ID")  # Revit parameter "Type Mark"
		elem_light_num = toolsrvt.get_parval(self.rvt_elem, "E_Light_number")
		self.params.append(["Type Mark", elem_mark + " "])
		self.params.append(["E_Light_number", str(elem_light_num) + " "])

class DiagFirst(Diagramm):
	def __init__(self, rvt_elem, column, row):
		super().__init__(rvt_elem, column, row)
		self.get_elem_symbol()

	def get_elem_symbol(self):
		self.symbol_type = self.type_first
		return self.type_first
	
	def calc_insert_point(self):
		super().calc_insert_point()
		new_pnt_X = self.insert_point.X - toolsrvt.mm_to_ft(1000)
		new_pnt_Y = self.insert_point.Y
		self.insert_point = XYZ(new_pnt_X, new_pnt_Y, 0)
	
	def get_params_to_set(self):
		circuit_inst = self.rvt_elem
		circuit_load_name = circuit_inst.LoadName

		circuit_wire_size = circuit_inst.WireSizeString
		circuit_wire_type = circuit_inst.WireType.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()

		if "#2.5" in circuit_wire_size and "NYM" in circuit_wire_type:
			circuit_wire_str = "NYM 3x2.5"
		elif "#2.5" in circuit_wire_size and "NHXH E30" in circuit_wire_type:
			circuit_wire_str = "NHXH E30 3x2.5"
		elif "4" in circuit_wire_size and "NYM" in circuit_wire_type:
			circuit_wire_str = "NYM 3x4"
		elif "4" in circuit_wire_size and "NHXH E30" in circuit_wire_type:
			circuit_wire_str = "NHXH E30 3x4"
		else:
			circuit_wire_str = ""

		self.params.append(["Beschriftung 1", circuit_load_name])
		self.params.append(["Beschriftung 2", circuit_wire_str])
