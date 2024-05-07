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
	# hard coded parameters
	circuits_param_to_set = ["RBS_ELEC_CIRCUIT_FRAME_PARAM"]
	panel_params_to_set = [
		"_Breaker_Type"
		"_IR(LTPU)", "_tr(LTD)",
		"_Isd(STPU)", "_tsd(STD)",
		"_Ii(INST)",
		"_Ig(GFPU)", "_tg(GFD)",
		"RBS_ELEC_CIRCUIT_FRAME_PARAM"]

	header_point = [-0.919769759118699, 1.86351706036745, 0]
	body_point = [-0.916488919223686, 1.63683154412002, 0]
	shedule_origin = [-1.15591572531952, 1.87274442257217, 0]
	step_y = 0.0623365636168
	header_symbol = None
	body_symbol = None
	foot_symbol = None

	def __init__(self, sheet_obj):
		self.sheet = sheet_obj
		self.insert_point = None
		self.params = list()
		self.symbol_type = None
		self.instance = None
		self.doc = sheet_obj.Document

	def create_elem_on_sheet(self):
		dia_inst = self.doc.Create.NewFamilyInstance(
			self.insert_point,
			self.symbol_type,
			self.sheet)
		return dia_inst

	def set_parameters(self):
		if not self.params or not self.instance:
			return None
		for param_info in self.params:
			param_name = param_info[0]
			param_val = param_info[1]
			toolsrvt.setup_param_value(
				self.instance,
				param_name,
				param_val)
		return param_name, param_val

	@classmethod
	def set_diag_types(cls, doc):
		cls.header_symbol = toolsrvt.type_by_bic_fam_type(
			doc,
			BuiltInCategory.OST_GenericAnnotation,
			"Panel main FD",
			"Panel main FD")

		cls.body_symbol = toolsrvt.type_by_bic_fam_type(
			doc,
			BuiltInCategory.OST_GenericAnnotation,
			"Panel FD",
			"Panel FD")

		cls.foot_symbol = toolsrvt.type_by_bic_fam_type(
			doc,
			BuiltInCategory.OST_GenericAnnotation,
			"Panel FD_Footer",
			"Panel FD_Footer")

	def get_circuit_symbol(self, circuit: Autodesk.Revit.DB.Electrical.ElectricalSystem):
		# NONE (Spare or Space)
		if circuit.CircuitType != Autodesk.Revit.DB.Electrical.CircuitType.Circuit:
			self.params.append(["Panel", 0])
			self.params.append(["POC", 0])
			self.params.append(["Socket", 0])
			self.params.append(["Wallbox", 0])
			self.params.append(["Reference", ""])
			return None

		# Check if element in the circuit is panel.
		# 1. Circuit contains only 1 element
		# 2. This element is electrical panel by category
		# 3. Element not Quasy
		circuit_first_element = list(circuit.Elements)[0]
		circ_name = str(circuit.LoadName).lower()
		elem_is_alone = len(list(circuit.Elements)) == 1  # 1
		elem_category = circuit_first_element.Category.Id == ElementId(-2001040)
		elem_not_quasy = "QUASI" not in circuit_first_element.Symbol.Family.Name
		elem_is_panel = all([elem_is_alone, elem_category, elem_not_quasy])
		elem_is_socket = True if "socket" in circ_name else False
		elem_is_wallbox = True if "wallbox" in circ_name else False

		if elem_is_panel:
			self.params.append(["Panel", 1])
			self.params.append(["POC", 0])
			self.params.append(["Socket", 0])
			self.params.append(["Wallbox", 0])

			# get reference
			refer_sheet = toolsrvt.inst_by_cat_strparamvalue(
				self.doc,
				BuiltInCategory.OST_Sheets,
				BuiltInParameter.SHEET_NAME,
				circuit.LoadName,
				False)

			if refer_sheet:
				refer_sheet = refer_sheet[0]
				refer_sheet_number = refer_sheet.SheetNumber
				self.params.append(["Reference", refer_sheet_number])
				return None
			else:
				self.params.append(["Reference", "N/A"])
				return None

		elif elem_is_socket:
			self.params.append(["Panel", 0])
			self.params.append(["POC", 0])
			self.params.append(["Socket", 1])
			self.params.append(["Wallbox", 0])
			self.params.append(["Reference", ""])
		
		elif elem_is_wallbox:
			self.params.append(["Panel", 0])
			self.params.append(["POC", 0])
			self.params.append(["Socket", 0])
			self.params.append(["Wallbox", 1])
			self.params.append(["Reference", ""])
		
		else:
			# POC symbol - all other
			self.params.append(["Panel", 0])
			self.params.append(["POC", 1])
			self.params.append(["Socket", 0])
			self.params.append(["Wallbox", 0])
			self.params.append(["Reference", ""])

	def get_header_info(self, panel_inst):
		circuits_all = toolsrvt.elsys_by_brd(panel_inst)
		circuits_main = circuits_all[0]
		self.insert_point = XYZ(
			self.header_point[0],
			self.header_point[1],
			self.header_point[2])
		self.symbol_type = self.header_symbol
		self.params = [[i, toolsrvt.get_parval(panel_inst, i)]
			for i in self.panel_params_to_set]

		# panel connected from
		if circuits_main:
			panel_connected_name = circuits_main.BaseEquipment.Name
			self.params.append(["Panel name", panel_connected_name])
		else:
			panel_connected_name = None

		# connected from panel - Refer to sheet name
		if panel_connected_name:
			panel_connected_sheet = toolsrvt.inst_by_cat_strparamvalue(
				self.doc,
				BuiltInCategory.OST_Sheets,
				BuiltInParameter.SHEET_NAME,
				panel_connected_name,
				False)
			if panel_connected_sheet:
				panel_connected_sheet_number = panel_connected_sheet[0].get_Parameter(
					BuiltInParameter.SHEET_NUMBER).AsString()
				self.params.append(["Reference", panel_connected_sheet_number])

		# circuit number
		circuits_main_number = circuits_main.CircuitNumber
		self.params.append(["RBS_ELEC_CIRCUIT_NUMBER", circuits_main_number])

	@classmethod
	def get_body_info(cls, sheet_obj, panel_inst):
		diagramm_list = list()
		circuits_all = toolsrvt.elsys_by_brd(panel_inst)
		circuits = circuits_all[1]
		# ================ BODY diagramms for circuits
		for i, circuit in enumerate(circuits):
			body_diag = Diagramm(sheet_obj)
			body_diag.params = [[
				i,
				toolsrvt.get_parval(circuit, i)]
				for i in Diagramm.circuits_param_to_set]

			step_current = body_diag.step_y * i
			body_diag.insert_point = XYZ(
				cls.body_point[0],
				cls.body_point[1] - step_current,
				cls.body_point[2])
			body_diag.symbol_type = cls.body_symbol
			body_diag.get_circuit_symbol(circuit)
			diagramm_list.append(body_diag)
		return diagramm_list

	@classmethod
	def get_footer_info(cls, sheet_obj, panel_inst):
		circuits_all = toolsrvt.elsys_by_brd(panel_inst)
		circuits = circuits_all[1]
		circuits_total = len(circuits)
		footer_diag = Diagramm(sheet_obj)
		footer_diag.symbol_type = cls.foot_symbol
		footer_diag.insert_point = XYZ(
			cls.body_point[0],
			cls.body_point[1] - cls.step_y * circuits_total,
			cls.body_point[2])
		return footer_diag

	@classmethod
	def get_ID_to_remove(cls, sheet_obj):
		doc = sheet_obj.Document
		# find instances to be removed
		filter_instance_header = FamilyInstanceFilter(doc, cls.header_symbol.Id)
		filter_instance_body = FamilyInstanceFilter(doc, cls.body_symbol.Id)
		filter_instance_footer = FamilyInstanceFilter(doc, cls.foot_symbol.Id)

		filter_all = LogicalOrFilter([filter_instance_body,
			filter_instance_header,
			filter_instance_footer])
		to_remove_id = sheet_obj.GetDependentElements(filter_all)
		return to_remove_id


def get_pairs(doc):
	# TODO make more universal method not only for 2C and 2A

	# get all panels
	c_panel_symbol_Id = toolsrvt.type_by_bic_fam_type(
		doc,
		BuiltInCategory.OST_ElectricalEquipment,
		"Switchboard",
		"TYPE 2C 1800x2200x600mm").Id

	a_panel_symbol_Id = toolsrvt.type_by_bic_fam_type(
		doc,
		BuiltInCategory.OST_ElectricalEquipment,
		"Switchboard",
		"TYPE 2A 1800x2200x600mm").Id

	# a_panel_symbol_Id = toolsrvt.type_by_bic_fam_type(
	# 	doc,
	# 	BuiltInCategory.OST_ElectricalEquipment,
	# 	"Switchboard",
	# 	"Chamber 200x2200x600mm").Id

	filter_panel_c = FamilyInstanceFilter(doc, c_panel_symbol_Id)
	filter_panel_a = FamilyInstanceFilter(doc, a_panel_symbol_Id)

	filter_or = LogicalOrFilter(
		filter_panel_c,
		filter_panel_a)

	panels_found = FilteredElementCollector(doc).\
		OfCategory(BuiltInCategory.OST_ElectricalEquipment).\
		WherePasses(filter_or).\
		ToElements()

	# if panel name in sheet name: create pair and add to pair list
	pairs = [[i, get_sheet_by_panel(i)[0]]
		for i in panels_found
		if get_sheet_by_panel(i)]
	return pairs


def get_sheet_by_panel(panel_inst):
	doc = panel_inst.Document
	panel_name = panel_inst.Name
	panel_connected_sheet = toolsrvt.inst_by_cat_strparamvalue(
		doc,
		BuiltInCategory.OST_Sheets,
		BuiltInParameter.SHEET_NAME,
		panel_name,
		False)
	return panel_connected_sheet
