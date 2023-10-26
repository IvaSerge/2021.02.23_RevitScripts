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

import pandas as pd

# ================ local imports
import toolsrvt
reload(toolsrvt)
from toolsrvt import *


def get_boq_by_elements(elems_list):

	# BOQ schedule
	# | Category | Description |
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

	return zip(out_categories, out_description, out_count)


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
	out_category = ["ElectricalSystem"] * len(out_cables)

	return zip(out_category, out_cables, out_length)
