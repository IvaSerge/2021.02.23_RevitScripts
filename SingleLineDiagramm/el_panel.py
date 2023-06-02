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
		total_panels = 0
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
	start_point = XYZ(-1.01165024787389, -0.284813943745498, 0)
	sheet: Autodesk.Revit.DB.ViewSheet

	def __init__(self, _rvt_panel):
		# type: (Autodesk.Revit.DB.Electrical.ElectricalEquipment) -> any
		"""
		Extended electrical panel class
		"""
		self.rvt_panel = _rvt_panel  # type: Autodesk.Revit.DB.Electrical.ElectricalEquipment
		self.index_row: int
		self.index_column: int
		self.circuits_to_check = toolsrvt.elsys_by_brd(_rvt_panel)[1]
		self.insert_point: XYZ
		self.annotation_type: Autodesk.Revit.DB.AnnotationSymbol
		self.annotation_inst: Autodesk.Revit.DB.AnnotationSymbol
		self.parameters_to_set = list()

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

	def point_by_index(self):
		doc = self.rvt_panel.Document
		x_shift = toolsrvt.mm_to_ft(doc, 65)
		y_shift = toolsrvt.mm_to_ft(doc, 20)
		point_x = self.start_point.X + self.index_column * x_shift
		point_y = self.start_point.Y - self.index_row * y_shift
		point_z = 0
		self.insert_point = XYZ(point_x, point_y, point_z)

	def get_anno_type(self):
		doc = self.rvt_panel.Document
		# Substation (main panel) type
		if self.index_column == 0 and self.index_row == 0:
			anno_type = toolsrvt.type_by_bic_fam_type(
				doc,
				BuiltInCategory.OST_GenericAnnotation,
				"2D_SLD_Panel",
				"LV_Switchgear")

		# Branch panel type
		else:
			anno_type = toolsrvt.type_by_bic_fam_type(
				doc,
				BuiltInCategory.OST_GenericAnnotation,
				"2D_SLD_Panel",
				"Branch")

		self.annotation_type = anno_type

	def create_elem_on_sheet(self):
		if not self.annotation_type:
			return None
		doc = self.rvt_panel.Document

		self.annotation_inst = doc.Create.NewFamilyInstance(
			self.insert_point,
			self.annotation_type,
			self.sheet)

	def find_elem_on_sheet(self):
		sheet = self.sheet
		self.annotation_inst = sheet
		doc = sheet.Document
		panel_name = self.parameters_to_set[1][1]
		circuit_number = self.parameters_to_set[5][1]

		fnrvStr = FilterStringEquals()

		pvpType = ParameterValueProvider(ElementId(int(BuiltInParameter.SYMBOL_NAME_PARAM)))
		pvpFam = ParameterValueProvider(ElementId(int(BuiltInParameter.ALL_MODEL_FAMILY_NAME)))

		fruleF = FilterStringRule(pvpFam, fnrvStr, "2D_SLD_Panel")
		filterF = ElementParameterFilter(fruleF)

		fruleT = FilterStringRule(pvpType, fnrvStr, "Branch")
		filterT = ElementParameterFilter(fruleT)

		filter = LogicalAndFilter(filterT, filterF)

		elems = FilteredElementCollector(doc, sheet.Id).\
			OfCategory(BuiltInCategory.OST_GenericAnnotation).\
			WhereElementIsNotElementType().\
			WherePasses(filter).\
			ToElements()

		if not elems:
			error_text = "No 2D symbols found on the sheet"
			raise ValueError(error_text)

		elems = [i for i in elems
			if all([
				toolsrvt.get_parval(i, "RBS_ELEC_PANEL_NAME") == panel_name,
				toolsrvt.get_parval(i, "RBS_ELEC_CIRCUIT_NUMBER") == circuit_number,
			])]
		if not elems:
			error_text = "Branch is new. Create new 2D tree"
			raise ValueError(error_text)

		self.annotation_inst = elems

	def get_distance_to_previous(self, panels_list, i_current):
		doc = self.rvt_panel.Document
		# that's a first element. Distance is not important
		if i_current == 0:
			return None

		current_panel_column = self.index_column
		current_panel_row = self.index_row
		# find previous panel
		for previous_panel in reversed(panels_list[0:i_current]):
			previous_panel_column = previous_panel.index_column
			previous_panel_row = previous_panel.index_row

			# distance column is +1
			panel_check = any([
				current_panel_column == previous_panel_column,
				current_panel_column == previous_panel_column + 1])

			if panel_check:
				previous_panel_row = previous_panel.index_row
				row_diff = current_panel_row - previous_panel_row

				if row_diff == 1 and current_panel_column == previous_panel_column + 1:
					return self.parameters_to_set.append(["L", toolsrvt.mm_to_ft(doc, 18.5)])

				else:
					distance = row_diff * toolsrvt.mm_to_ft(doc, 20)
					return self.parameters_to_set.append(["L", distance])

	def set_parameters(self):
		if not self.parameters_to_set:
			return None

		for par_name, par_value in self.parameters_to_set:
			toolsrvt.setup_param_value(
				self.annotation_inst,
				par_name,
				par_value)

	def get_panel_parameters(self):
		# instance parameters
		params_to_read = [
			"RBS_ELEC_PANEL_NAME",
			"_Breaker_Type",
			"_Ii(INST)",
			"_IR(LTPU)",
			"_Isd(STPU)",
			"_tr(LTD)",
			"_tsd(STD)"]

		params_to_set = [
			"RBS_ELEC_PANEL_NAME",
			"_Breaker_Type_Panel",
			"_Ii(INST)_Panel",
			"_IR(LTPU)_Panel",
			"_Isd(STPU)_Panel",
			"_tr(LTD)_Panel",
			"_tsd(STD)_Panel"]

		for p_to_reed, p_to_set in zip(params_to_read, params_to_set):
			try:
				p_val = toolsrvt.get_parval(self.rvt_panel, p_to_reed)
				if p_val:
					self.parameters_to_set.append([p_to_set, p_val])
			except:
				continue

		# type parameters
		panel_symbol = self.rvt_panel.Symbol
		panel_type = panel_symbol.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()
		self.parameters_to_set.append(["ALL_MODEL_TYPE_NAME", panel_type])

	def get_circuit_parameters(self):
		circuit = toolsrvt.elsys_by_brd(self.rvt_panel)[0]

		if not circuit:
			return None

		params_to_read = [
			"RBS_ELEC_CIRCUIT_LENGTH_PARAM",
			"RBS_ELEC_CIRCUIT_WIRE_SIZE_PARAM",
			"RBS_ELEC_CIRCUIT_NUMBER",
			"_Breaker_Type",
			"_Ii(INST)",
			"_IR(LTPU)",
			"_Isd(STPU)",
			"_tr(LTD)",
			"_tsd(STD)"]
		param_values = [toolsrvt.get_parval(circuit, p_name) for p_name in params_to_read]
		self.parameters_to_set.extend(zip(params_to_read, param_values))

	def get_control_circuit_parameters(self):
		allsys = self.rvt_panel.MEPModel.GetElectricalSystems()
		circuits = [i for i in allsys if i.SystemType == Electrical.ElectricalSystemType.Controls]

		if not circuits:
			return None

		circuit = circuits[0]

		params_to_read = [
			"_Breaker_Type",
			"_Ii(INST)",
			"_IR(LTPU)",
			"_Isd(STPU)",
			"_tr(LTD)",
			"_tsd(STD)"]

		params_to_set = [
			"_Breaker_Type_Panel",
			"_Ii(INST)_Panel",
			"_IR(LTPU)_Panel",
			"_Isd(STPU)_Panel",
			"_tr(LTD)_Panel",
			"_tsd(STD)_Panel"]

		param_values = [toolsrvt.get_parval(circuit, p_name) for p_name in params_to_read]
		self.parameters_to_set.extend(zip(params_to_set, param_values))
