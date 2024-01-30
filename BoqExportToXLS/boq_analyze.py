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

# ================ local imports
import toolsrvt
reload(toolsrvt)
from toolsrvt import *


def get_boq_by_elements(elems_list: list) -> list:

	# BOQ schedule
	# | Category | Description |
	if not elems_list:
		return list()

	elem_id = [i.Id.IntegerValue for i in elems_list]
	elem_categories = [i.Category.Name for i in elems_list]
	elem_description = [
		toolsrvt.get_parval(i.Symbol, "ALL_MODEL_DESCRIPTION")
		for i in elems_list]

	pd_elem_ids = pd.Series(elem_id)
	pd_cats = pd.Series(elem_categories)
	pd_des = pd.Series(elem_description)

	pd_elems_frame = pd.DataFrame({
		"Element Id": pd_elem_ids,
		"Category": pd_cats,
		"Description": pd_des})

	df_groupped_by = pd_elems_frame.groupby(["Category", "Description"])["Description"].indices.keys()

	out_categories = [i[0] for i in df_groupped_by]
	out_description = [i[1] for i in df_groupped_by]
	out_count = pd_elems_frame.groupby(["Category", "Description"]).size().tolist()

	return list(zip(out_categories, out_description, out_count))


def get_wire_type(el_circuit):

	circuit_system_type = el_circuit.SystemType
	# for electrical circuit
	if circuit_system_type == Electrical.ElectricalSystemType.PowerCircuit:
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
			# TODO: Check cable description
			# for specific cable sizing, for example, single core, or control cable
			# see "Cable Description" parameter.

		return circuit_wire + " " + circuit_wire_size

	elif circuit_system_type == Electrical.ElectricalSystemType.Data:
		# for DATA circuit
		return "LAN 250 (S/FTP) CAT.6A"

	else:
		return None


def get_wire_length(el_circuit):
	doc = el_circuit.Document
	circuit_length = el_circuit.Length
	length_m = round(toolsrvt.ft_to_mm(doc, circuit_length) / 1000)
	return length_m


def get_boq_by_circuits(el_circuits):

	if not el_circuits:
		return list()

	elem_id = [i.Id.IntegerValue for i in el_circuits]
	sys_wire_types = [get_wire_type(i) for i in el_circuits]
	sys_length = [get_wire_length(i) for i in el_circuits]

	pd_elem_ids = pd.Series(elem_id)
	pd_wire = pd.Series(sys_wire_types)
	pd_length = pd.Series(sys_length)

	pd_wires_frame = pd.DataFrame({
		"Element Id": pd_elem_ids,
		"Wire Type": pd_wire,
		"Length": pd_length})

	df_groupped_by = pd_wires_frame.groupby("Wire Type")["Wire Type"].indices.keys()
	out_cables = [i for i in df_groupped_by]
	out_length = pd_wires_frame.groupby("Wire Type")["Length"].sum().tolist()
	out_category = ["Cables"] * (len(out_cables))
	out_length_spare = [round(i * 1.2) for i in out_length]

	return zip(out_category, out_cables, out_length, out_length_spare)


def sorted_by_category(list_of_lists):
	"""Groups list by category where:\\
		key is list[0], values are list[1:]
	"""
	result_dict = dict()

	for lst in list_of_lists:
		if not result_dict.get(lst[0]):
			# new value
			result_dict.update({lst[0]: [lst[1:]]})

		else:
			# value exists
			current_val = [i for i in result_dict.get(lst[0])] + ([lst[1:]])
			result_dict.update({lst[0]: current_val})

	return sorted(list(result_dict.items()), key=lambda x: x[0])


def get_boq_by_l_based_fam(l_based_families):

	if not l_based_families:
		return list()

	doc = l_based_families[0].Document

	lbf_description = [
		get_lbf_description(i)
		for i in l_based_families]

	lbf_length = [
		math.ceil((ft_to_mm(doc, get_parval(i, "CURVE_ELEM_LENGTH")) / 1000))
		for i in l_based_families]

	lbf_cat = [i.Category.Name for i in l_based_families]

	pd_cat = pd.Series(lbf_cat)
	pd_descr = pd.Series(lbf_description)
	pd_length = pd.Series(lbf_length)
	pd_frame = pd.DataFrame({
		"Category": pd_cat,
		"Description": pd_descr,
		"Length": pd_length})

	df_groupped_by = pd_frame.groupby(["Category", "Description"])["Description"].indices.keys()
	out_category = [i[0] for i in df_groupped_by]
	out_description = [i[1] for i in df_groupped_by]
	out_length = pd_frame.groupby(["Category", "Description"])["Length"].sum().tolist()

	return zip(out_category, out_description, out_length)


def get_boq_by_tray_fitting(fitting_list):
	if not fitting_list:
		return list()

	tray_description = [
		get_fitting_description(i)
		for i in fitting_list
		if "union" not in str.lower(get_fitting_description(i))]

	# TODO: Replace Reuced T and X with Add-ons
	pd_tray = pd.Series(tray_description)
	pd_tray_frame = pd.DataFrame({
		"Description": pd_tray})

	df_groupped_by = pd_tray_frame.groupby("Description")["Description"].indices.keys()
	out_trays = [i for i in df_groupped_by]
	out_size = pd_tray_frame.groupby("Description")["Description"].size().tolist()
	out_category = ["Cable tray fittings"] * (len(fitting_list) - 1)
	return zip(out_category, out_trays, out_size)


def add_headers(boq_list: list) -> list:
	"""Add headers and empty cells to follow general standard"""

	boq_updated = list()
	for boq in boq_list:
		category = boq[0]
		elements = boq[1]

		# boq in excel consists of 3 columns.
		# frist line
		boq_first = [category, [], []]

		# second line is different for differend categories:
		if category == "Cables":
			boq_second = ["Wire Type", "Length [m]", "Length with Spare 20% [m]"]

		elif category == "Cable trays":
			boq_second = ["Description, Size WxH", "Length [m]", "Comments"]

		elif category == "Cable tray fittings":
			boq_second = ["Description, Size WxH", "Count", "Comments"]

		else:
			boq_second = ["Description", "Count", "Comments"]

		boq_cat_list = list()
		boq_cat_list.append(boq_first)
		boq_cat_list.append(boq_second)
		boq_cat_list.extend(elements)

		boq_updated.append(boq_cat_list)

	return boq_updated


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

	# TODO: analyze Reudcer, T and X with reduced parts
	# analyzing model string to get decription and H
	regexp = re.compile(r"^(.*)\s(H\d*)")  # or take firs two symbols
	check = regexp.match(fitting_model)
	fitting_descr = check.group(1)
	fitting_h = check.group(2)

	# analyzing instance size to get width
	fitting_size = get_parval(rvt_fitting, "RBS_CALCULATED_SIZE")
	regexp = re.compile(r"^\d*")  # or take firs two symbols
	fitting_w = regexp.search(fitting_size).group(0)

	fitting_out = f"{fitting_descr} W{fitting_w} {fitting_h}"
	return fitting_out
