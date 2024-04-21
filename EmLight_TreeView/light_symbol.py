import clr

# ================ Revit imports
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager


# ================ local imports
import toolsrvt
from toolsrvt import *
import elsys_extend
from elsys_extend import *


class LightSymbol():
	start_point: XYZ = None
	current_row: int = 0
	current_column: int = 0
	types_list = []

	def __init__(self, _rvt_inst):
		self.rvt_inst = _rvt_inst
		self.type_2D: FamilyType = None
		self.inst_2D: FamilyInstance = None
		self.insert_point: XYZ = None
		self.slot: list[int] = None

	@classmethod
	def get_symbols_types(cls, doc):
		"""
			This method runs only once and provide
			2D types in class variable types_list.
			types_list can be accessable via other methods
		"""

		type_first = toolsrvt.type_by_bic_fam_type(
			doc,
			BuiltInCategory.OST_DetailComponents,
			"2D_NOT_Steigzonen",
			"2D_diagramm_NOT_1P")

		type_emergency = toolsrvt.type_by_bic_fam_type(
			doc,
			BuiltInCategory.OST_DetailComponents,
			"2D_NOT_Shema",
			"2D_diagramm_E01")

		type_exit = toolsrvt.type_by_bic_fam_type(
			doc,
			BuiltInCategory.OST_DetailComponents,
			"2D_NOT_Shema",
			"2D_diagramm_Exit")

		type_box = toolsrvt.type_by_bic_fam_type(
			doc,
			BuiltInCategory.OST_DetailComponents,
			"2D_NOT_Shema",
			"2D_junction_box")

		cls.types_list.append(type_first)
		cls.types_list.append(type_emergency)
		cls.types_list.append(type_exit)
		cls.types_list.append(type_box)

			
	def get_symbol_by_rvt_elem(self):
		elem = self.rvt_inst
		elem_type_mark = get_parval(elem.Symbol, "WINDOW_TYPE_ID")  # Revit parameter "Type Mark"

		# junction box
		if not elem_type_mark:
			self.type_2D = self.types_list[3]

		# exit sign
		elif any(["03" in elem_type_mark, "04" in elem_type_mark, "06" in elem_type_mark]):
			self.type_2D = self.types_list[2]

		# emergency light
		else:
			self.type_2D = self.types_list[1]

	def create_2D(self, rvt_view):
		insert_pnt = self.insert_point
		symbol_type: FamilyType = self.type_2D
		doc = symbol_type.Document
		instance_on_view = doc.Create.NewFamilyInstance(
			insert_pnt,
			symbol_type,
			rvt_view)
		self.inst_2D = instance_on_view
		return instance_on_view

	@staticmethod
	def get_first_symbol(_rvt_circuit):
		first_sym = LightSymbol(None)
		first_sym.type_2D = first_sym.types_list[0]
		first_sym.insert_point = first_sym.start_point
		# get circuit parameters to be written in 2D
		# get cable type
		# get cable length
		# get circuit name
		return first_sym

	def get_insert_point_by_index(self):
		doc = self.type_2D.Document
		current_row = self.slot[0]
		current_column = self.slot[1]
		start_point: XYZ = self.start_point
		start_x = start_point.X
		start_y = start_point.Y
		current_x = start_x + toolsrvt.mm_to_ft(doc, 1000) * current_column
		current_y = start_y + toolsrvt.mm_to_ft(doc, 2000) * current_row
		current_xyz = XYZ(current_x, current_y, 0)
		self.insert_point = current_xyz


	@staticmethod
	def get_all_symbols_by_circuit(_rvt_circuit, start_slot):
		doc = _rvt_circuit.Document
		start_row = start_slot[0]
		start_column = start_slot[1]
		rvt_elems = elsys_extend.get_sorted_circuit_elements(_rvt_circuit)
		symbols = [LightSymbol(i) for i in rvt_elems]

		# define slot numbers using level occupancy list
		for i, symbol in enumerate(symbols):
			symbol.slot = [start_row, start_column + i]
			symbol.get_symbol_by_rvt_elem()  # get 2D for a symbol
			symbol.get_insert_point_by_index()
			# get symbol parameters
			# convert slot-numbers to insert points
		

		# update occupancy list
		# update element parameters

		return symbols
