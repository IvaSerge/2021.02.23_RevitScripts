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
		self.grid_row: int = None
		self.grid_column: int = None

	@classmethod
	def get_symbols_types(cls, doc):

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

		cls.types_list.append(type_first)
		cls.types_list.append(type_emergency)
		cls.types_list.append(type_exit)

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

	@staticmethod
	def get_all_symbols_by_circuit(_rvt_circuit, start_slot):
		# get all elements of the circuit
		rvt_elems = elsys_extend.get_sorted_circuit_elements(_rvt_circuit)
		# sort elements by length along circuit path
		# define slot numbers using level occupancy list
		# convert slot-numbers to insert points
		# update occupancy list
		# update element parameters

		return rvt_elems
