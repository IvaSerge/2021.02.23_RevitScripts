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
	circuit_usv_number: int = int()
	types_list = []
	circuit_symbols: list = []

	def __init__(self, _rvt_inst):
		self.rvt_inst = _rvt_inst
		self.type_2D: FamilyType = None
		self.inst_2D: FamilyInstance = None
		self.insert_point: XYZ = None
		self.slot: list[int] = None
		self.params_to_set = list()

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

	def get_light_parameters(self):
		rvt_elem = self.rvt_inst
		circuit_usv_num = self.circuit_usv_number

		# get symbol parameters
		elem_mark = get_parval(rvt_elem.Symbol, "WINDOW_TYPE_ID")  # Revit parameter "Type Mark"
		elem_light_num = get_parval(rvt_elem, "E_Light_number")

		self.params_to_set.append(["Type Mark", elem_mark])
		self.params_to_set.append(["Panel", circuit_usv_num])
		self.params_to_set.append(["E_Light_number", elem_light_num])

	def get_box_parameters(self):
		return None

		
	def get_symbol_by_rvt_elem(self):
		elem = self.rvt_inst
		elem_type_mark = get_parval(elem.Symbol, "WINDOW_TYPE_ID")  # Revit parameter "Type Mark"

		# junction box
		if not elem_type_mark:
			self.type_2D = self.types_list[3]
			self.get_box_parameters()

		# exit sign
		elif any(["03" in elem_type_mark, "04" in elem_type_mark, "06" in elem_type_mark]):
			self.type_2D = self.types_list[2]
			self.get_light_parameters()

		# emergency light
		else:
			self.type_2D = self.types_list[1]
			self.get_light_parameters()

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
	
	def set_parameters(self):
		if not self.params_to_set:
			return None

		symbol_2D = self.inst_2D
		for param_info in self.params_to_set:
			param_name = param_info[0]
			param_val = param_info[1]
			toolsrvt.setup_param_value(symbol_2D, param_name,param_val)

	@staticmethod
	def get_first_symbol(_rvt_circuit):
		doc = _rvt_circuit.Document
		first_sym = LightSymbol(None)
		first_sym.type_2D = first_sym.types_list[0]
		first_sym.insert_point = first_sym.start_point
		# get circuit parameters to be written in 2D
		circuit_name = _rvt_circuit.LoadName
		circuit_cable = elsys_extend.get_cable_name(_rvt_circuit)
		circuit_length = toolsrvt.ft_to_mm(
			doc,
			toolsrvt.get_parval(_rvt_circuit, "RBS_ELEC_CIRCUIT_LENGTH_PARAM"))
		circuit_length = round(circuit_length/1000)
		length_txt = f"L = {circuit_length}m"

		#append info to symbol parameters to set list
		first_sym.params_to_set.append(["Beschriftung 1", circuit_name])
		first_sym.params_to_set.append(["Beschriftung 2", circuit_cable])
		first_sym.params_to_set.append(["Beschriftung 3", length_txt])
		return first_sym

	def get_insert_point_by_index(self):
		doc = self.type_2D.Document
		current_column = self.slot[0]
		current_row = self.slot[1]
		start_point: XYZ = self.start_point
		start_x = start_point.X
		start_y = start_point.Y
		current_x = start_x + toolsrvt.mm_to_ft(doc, 1000) * current_column
		current_y = start_y - toolsrvt.mm_to_ft(doc, 1500) * current_row
		current_xyz = XYZ(current_x, current_y, 0)
		self.insert_point = current_xyz

	@classmethod
	def check_next_slot(cls, current_slot, slots_needed):
		elems_on_current_row = [i.slot for i in cls.circuit_symbols if i.slot[1] == current_slot[1]]

		# current row is empty - all good
		if not elems_on_current_row:
			return current_slot

		# current row is occupied - find occupied slot.
		filtered_first_row = [i.slot for i in cls.circuit_symbols if i.slot[1] != 0]

		# We do not care, if top rows are occupied. Only bottom rows are important
		colums_occupied = [i[0] for i in filtered_first_row if i[1] >= current_slot[1]]
		minimal_occupied_slot = min(colums_occupied)
		
		if current_slot[0] + slots_needed < minimal_occupied_slot:
			return current_slot

		else:
			# check next row
			return LightSymbol.check_next_slot([current_slot[0], current_slot[1] + 1], slots_needed)


	@staticmethod
	def get_all_symbols_by_circuit(_rvt_circuit, start_slot):
		start_column = start_slot[0]
		start_row = start_slot[1]
		rvt_elems = elsys_extend.get_sorted_circuit_elements(_rvt_circuit)
		symbols = [LightSymbol(i) for i in rvt_elems]
		LightSymbol.circuit_symbols.extend(symbols)

		for i, symbol in enumerate(symbols):
			symbol.slot = [start_column + i, start_row	]
			symbol.get_symbol_by_rvt_elem()  # get 2D for a symbol
			symbol.get_insert_point_by_index()

		# analyze all the symbols if there is a junction box
		# that means that revit instance category is Electrical Equipment
		for symbol in reversed(symbols):
			if symbol.rvt_inst.Category.Id.IntegerValue == -2001040:
				# get next circuits to analyze
				next_systems = toolsrvt.elsys_by_brd(symbol.rvt_inst)[1]
				start_column = symbol.slot[0] + 1
				system_row = start_row
				if not next_systems:
					continue
				for j, el_sys in enumerate(next_systems, start=1):
					# find next slot
					system_row = start_row + j
					system_column = start_column
					system_slots_needed = len([i for i in el_sys.Elements])
					slot_to_check = [system_column, system_row]
					checked_slot = LightSymbol.check_next_slot(slot_to_check, system_slots_needed)
					# start recursion
					LightSymbol.get_all_symbols_by_circuit(el_sys, checked_slot)

	@classmethod
	def calc_symbol_row(cls):
		# calculate level of the junction box
		all_symbols: list[LightSymbol] = cls.circuit_symbols
		for symbol in all_symbols:
			rvt_inst = symbol.rvt_inst
			if not rvt_inst:
				continue
			if symbol.rvt_inst.Category.Id.IntegerValue == -2001040:
				current_column = symbol.slot[0]
				current_row = symbol.slot[1]
				elems_on_next_column = [i.slot for i in cls.circuit_symbols if i.slot[0] == current_column + 1]
				rows_occupied = [i[1] for i in elems_on_next_column if i[1] > current_row]
				min_row = min(rows_occupied)

				# check how much circuits connected to junction box
				additional_rows = len(toolsrvt.elsys_by_brd(rvt_inst)[1]) - 1
				level_to_set = min_row - current_row + additional_rows
				symbol.params_to_set.append(["Number_of_rows", int(level_to_set)])

