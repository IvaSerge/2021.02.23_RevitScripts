import clr
import os
import sys

local_data = os.getenv("LOCALAPPDATA")
dyn_path = r"\python-3.9.12-embed-amd64\Lib"
py_path = local_data + dyn_path
sys.path.append(py_path)


# ================ Revit imports
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# ================ Python imports
from System import Array
from System.Collections.Generic import *
from importlib import reload
import re
import pandas as pd
import operator

# ================ local imports
import toolsrvt
reload(toolsrvt)
from toolsrvt import *
from rvt_obj_group import *



def get_wire_type(el_circuit):
	circuit_system_type = el_circuit.SystemType
	is_electrical = circuit_system_type == Electrical.ElectricalSystemType.PowerCircuit
	is_data = circuit_system_type == Electrical.ElectricalSystemType.Data
	have_description = toolsrvt.get_parval(el_circuit, "Cable Description") is not None
	# elec_non_standard_cable = is_electrical and have_description
	elec_non_standard_cable = have_description
	elec_standard_cable = is_electrical and not have_description

	if elec_standard_cable:
		circuit_wire = el_circuit.WireType
		if circuit_wire:
			circuit_wire = toolsrvt.get_parval(
				el_circuit.WireType,
				"SYMBOL_NAME_PARAM")
		else:
			circuit_wire = ""

		# remove last dot symbol. Project specific adjustment
		if circuit_wire and circuit_wire[-1] == ".":
			circuit_wire = circuit_wire[:-1]

		circuit_wire_size = el_circuit.WireSizeString
		if not circuit_wire_size:
			circuit_wire_size = ""

		return circuit_wire + " " + circuit_wire_size

	elif elec_non_standard_cable:
		return toolsrvt.get_parval(el_circuit, "Cable Description")

	# elif is_data:
	# 	return "LAN 250 (S/FTP) CAT.6A"

	else:
		return None


def get_wire_length(el_circuit):
	doc = el_circuit.Document
	circuit_length = el_circuit.Length
	length_m = round(toolsrvt.ft_to_mm(doc, circuit_length) / 1000)
	return length_m


def sort_cables_by_wire_size(cable_string: str):
	regexp = re.compile(r"^(.*?)\s\d-#(\d+.?\d?),")
	check = regexp.match(cable_string)
	if check:
		cable_name = check.group(1)
		cable_size = check.group(2)
		return (cable_name, float(cable_size))
	return (cable_string, 1000)


def get_boq_by_circuits(el_circuits):

	if not el_circuits:
		return list()

	elem_id = [i.Id.IntegerValue for i in el_circuits]
	sys_wire_types = [get_wire_type(i) for i in el_circuits]
	sys_length = [get_wire_length(i) for i in el_circuits]
	sys_change_num = [toolsrvt.get_parval(i, "BOQ Phase") for i in el_circuits]

	pd_elem_ids = pd.Series(elem_id)
	pd_wire = pd.Series(sys_wire_types)
	pd_length = pd.Series(sys_length)
	pd_change_num = pd.Series(sys_change_num)

	pd_wires_frame = pd.DataFrame({
		"Element Id": pd_elem_ids,
		"Wire Type": pd_wire,
		"Length": pd_length,
		"Change_num": pd_change_num})

	df_groupped_by = pd_wires_frame.groupby(["Wire Type", "Change_num"])["Wire Type"].indices.keys()
	out_cables = [i[0] for i in df_groupped_by]
	out_change_num = [i[1] for i in df_groupped_by]
	out_length = pd_wires_frame.groupby("Wire Type")["Length"].sum().tolist()
	out_length_spare = [round(i * 1.2) for i in out_length]
	cables_list = list(zip(out_cables, out_length, out_length_spare, out_change_num))

	return sorted(cables_list, key=lambda x: sort_cables_by_wire_size(x[0]))

def get_boq_by_l_based_fam(l_based_families):

	if not l_based_families:
		return list()

	doc = l_based_families[0].Document

	lbf_description = [
		get_lbf_description(i)
		for i in l_based_families]

	lbf_length = [
		ft_to_mm(doc, get_parval(i, "CURVE_ELEM_LENGTH"))
		for i in l_based_families]

	lbf_cat = [i.Category.Name for i in l_based_families]

	lbf_manufacturer = [
		toolsrvt.get_parval(
			doc.GetElement(i.GetTypeId()),
			"ALL_MODEL_MANUFACTURER")
		for i in l_based_families]
	
	lbf_change_num = [
		toolsrvt.get_parval(
			i,
			"BOQ Phase")
		for i in l_based_families]

	pd_cat = pd.Series(lbf_cat)
	pd_descr = pd.Series(lbf_description)
	pd_length = pd.Series(lbf_length)
	pd_manufacturer = pd.Series(lbf_manufacturer)
	pd_change_num = pd.Series(lbf_change_num)
	pd_frame = pd.DataFrame({
		"Category": pd_cat,
		"Description": pd_descr,
		"Manufacturer": pd_manufacturer,
		"Length": pd_length,
		"Change_num": pd_change_num})

	df_groupped_by = pd_frame.groupby(["Category", "Description", "Manufacturer", "Change_num"])["Description"].indices.keys()
	out_description = [i[1] for i in df_groupped_by]
	out_manufacturer = [i[2] for i in df_groupped_by]
	length_mm = pd_frame.groupby(["Category", "Description"])["Length"].sum().tolist()
	out_length = [math.ceil(i/1000) for i in length_mm]
	out_change_num = [i[3] for i in df_groupped_by]

	return zip(out_description, out_length, out_manufacturer, out_change_num)

def get_boq_by_tray_fitting(fitting_list):
	if not fitting_list:
		return list()

	# filter out unions
	fittings_filtered = [i for i in fitting_list if 
		"union" not in str.lower(i.Symbol.Family.Name)]

	fitting_description = [
		get_fitting_description(i)
		for i in fittings_filtered]

	fitting_len = len(fitting_description)
	fitting_category = ["Cable tray fittings"] * fitting_len

	fitting_manufacurer = [
		toolsrvt.get_parval(i.Symbol, "ALL_MODEL_MANUFACTURER")
		for i in fittings_filtered]
	
	lbf_change_num = [
		toolsrvt.get_parval(
			i,
			"BOQ Phase")
		for i in fittings_filtered]

	out_list = list(zip(fitting_category, fitting_description, fitting_manufacurer, lbf_change_num))
	return out_list

def get_lbf_description(line_based_family):
	# get tray model, width, height and combine in string
	doc = line_based_family.Document
	lbf_type = doc.GetElement(line_based_family.GetTypeId())
	lbf_model = toolsrvt.get_parval(lbf_type, "ALL_MODEL_MODEL")

	# for rectangular element
	try:
		lbf_w = round(toolsrvt.ft_to_mm(doc, line_based_family.Width))
		lbf_h = round(toolsrvt.ft_to_mm(doc, line_based_family.Height))
		lbf_descr = f"{lbf_model} W{lbf_w} H{lbf_h}"
	except:
		# for round element
		try:
			lbf_d =  round(toolsrvt.ft_to_mm(doc, line_based_family.Diameter))
			# diameter need to be written in Model parameter
			lbf_descr = f"{lbf_model}"
		except:
			raise ValueError("Wrong element dimention")

	return lbf_descr


def get_fitting_description(rvt_fitting):
	fitting_symbol = rvt_fitting.Symbol
	fitting_model = get_parval(fitting_symbol, "ALL_MODEL_MODEL")
	check = None

	# analyzing model string to get decription and H
	regexp = re.compile(r"^(.*)\s(H\d*)")  # or take firs two symbols
	if fitting_model:
		check = regexp.match(fitting_model)
	if check:
		fitting_descr = check.group(1)
		fitting_h = check.group(2)
	else:
		fitting_Id = rvt_fitting.Id.IntegerValue
		error_string = f"Not standard fitting. Check ID: {fitting_Id}"
		print(error_string)
		raise ValueError(error_string)

	# analyzing instance size to get width
	fitting_size = get_parval(rvt_fitting, "RBS_CALCULATED_SIZE")
	regexp = re.compile(r"^\d*")  # or take firs two symbols
	fitting_w = regexp.search(fitting_size).group(0)

	fitting_out = f"{fitting_descr} W{fitting_w} {fitting_h}"
	return fitting_out

def get_sheets_by_seq_number(doc, rev_seq_number):

	revisions = FilteredElementCollector(doc).\
		OfClass(Autodesk.Revit.DB.Revision).\
		ToElements()
	revision = [i for i in revisions if i.SequenceNumber == rev_seq_number][0]

	rvt_sheets = FilteredElementCollector(doc).\
		OfCategory(BuiltInCategory.OST_Sheets).\
		WhereElementIsNotElementType().\
		ToElements()

	out_list = [] # for sheet in rvt_sheets:
	for sheet in rvt_sheets:
		rev_on_sheet = [doc.GetElement(i).SequenceNumber for i in sheet.GetAllRevisionIds() if i]

		if rev_seq_number in rev_on_sheet:
			out_list.append([
				sheet.SheetNumber,
				sheet.Name,
				sheet.GetRevisionNumberOnSheet(revision.Id)])

	if not out_list:
		return None
	else:
		return sorted(out_list, key=operator.itemgetter(0))

def get_boq_list_by_dcn(dcn_string: str):
	"""
		Creates a list to be write to excel file
	"""

	RvtObjGroup.boq_param_value = dcn_string

	elec_bic_list = (
		"OST_ConduitFitting",
		"OST_ElectricalEquipment",
		"OST_ElectricalFixtures",
		"OST_FireAlarmDevices",
		"OST_GenericModel",
		"OST_LightingDevices",
		"OST_LightingFixtures",
		"OST_NurseCallDevices",
		"OST_DuctFitting")

	boq_data= data_objects()
	boq_electrical = [electrical_objects(i) for i in elec_bic_list]

	boq_general = []
	boq_general.extend(boq_electrical)
	boq_general.append(boq_data)
	boq_general = sorted(boq_general)

	boq_trays = tsla_trays()
	boq_fittings = tsla_fittings()
	boq_cables = electrical_circuits()
	boq_cables.get_boq()
	boq_grounding = conduit_as_grounding()

	boq_list = []
	boq_list.extend(boq_general)
	boq_list.append(boq_cables)
	boq_list.append(boq_trays)
	boq_list.append(boq_fittings)
	boq_list.append(boq_grounding)
	boq_list = [i for i in boq_list if i.boq]

	return boq_list

def get_circuits_by_dcn(dcn_string: str):
	electrical_circuits.boq_param_value = dcn_string
	rvt_sys = electrical_circuits().get_circuits_list()
	if not rvt_sys:
		return None
	
	sys_type = [i.get_Parameter(BuiltInParameter.RBS_ELEC_CIRCUIT_TYPE).AsValueString() for i in rvt_sys]
	sys_panel = [i.get_Parameter(BuiltInParameter.RBS_ELEC_CIRCUIT_PANEL_PARAM).AsValueString() for i in rvt_sys]
	sys_circuit_number = [i.get_Parameter(BuiltInParameter.RBS_ELEC_CIRCUIT_NUMBER).AsValueString() for i in rvt_sys]
	sys_circuit_slot = [i.StartSlot for i in rvt_sys]
	sys_load_name = [i.get_Parameter(BuiltInParameter.RBS_ELEC_CIRCUIT_NAME).AsValueString() for i in rvt_sys]
	sys_wire_types = [get_wire_type(i) for i in rvt_sys]
	sys_length = [str(math.ceil(get_wire_length(i) * 1.2)) for i in rvt_sys]
	sys_change_num = [toolsrvt.get_parval(i, "BOQ Phase") for i in rvt_sys]
	# comments = [" "] * len(rvt_sys)

	pd_type = pd.Series(sys_type)
	pd_panel = pd.Series(sys_panel)
	pd_circuit_number = pd.Series(sys_circuit_number)
	pd_circuit_slot = pd.Series(sys_circuit_slot)
	pd_load_name = pd.Series(sys_load_name)
	pd_wire_types = pd.Series(sys_wire_types)
	pd_length = pd.Series(sys_length)
	pd_change_num = pd.Series(sys_change_num)
	pd_frame = pd.DataFrame({
		"CircuitType": pd_type,
		"PanelName": pd_panel,
		"CircuitN": pd_circuit_number,
		"CircuitS": pd_circuit_slot,
		"LoadName": pd_load_name,
		"WireType": pd_wire_types,
		"Length": pd_length,
		"Change_num": pd_change_num})

	# sort circuits
	pd_frame_sorted = pd_frame.sort_values(by=["CircuitType","PanelName","CircuitS"])
	grouped_list = pd_frame_sorted.groupby("PanelName")[
			["PanelName", "CircuitN", "LoadName", "WireType", "Length", "Change_num"]
		].apply(lambda x: x.values.tolist()).tolist()
	
	list_with_headers = [circuits_add_header(i) for i in grouped_list]

	return list_with_headers

def circuits_add_header(circuits_list):
	panel_name = circuits_list[0][0]
	first_row_header = f"Panel {panel_name} circuits"
	first_row = [first_row_header, "", "", "", "", "", ""]
	second_row = ["Panel", "Circuit", "Load name", "Wire", "L,m", "DCN", "Comments"]
	extend_list = [first_row, second_row]
	extend_list.extend(circuits_list)
	return extend_list