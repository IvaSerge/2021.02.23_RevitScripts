import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)


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

# ================ Python imports
import System
from System import Array
from System.Collections.Generic import *

from pathlib import Path

import csv
import re

import toolsrvt


def get_breakers_info(csv_breakers):
	# type: (Path) -> list[str]
	"""Get parametrs of circuit breakers from csv

	args:
		csv_breakers - path to csv file
	return:
		cbreakers_list - list of settings
	"""

	cbreakers_list = list()
	re_circuit_number = re.compile(r"(?<=\[).*(?=\])")
	re_panel_name = re.compile(r".+(?=\[)")

	breaker_trips = {
		"3WL13634NG611AA2": "ETU76B",  # 5000A in substation
		"3WL12323NG611AA2": "ETU76B",  # 3200A in substation
		"3WL11163NG611AA2": "ETU76B",  # 1600A in substation
		"3WL11163CB611AA2": "ETU25B",  # 1600A in distribution panel
		"3WA12204AF010AA0": "ETU600",  # 2000A
		"3WA12203AE010AA0": "ETU600",  # 2000A
		"3VA25106JP320AA0": "ETU550",  # 1000A
		"3VA24636KP320AA0": "ETU850",  # 630A
		"3VA23406KP320AA0": "ETU850",  # 400A
		"3VA22256KP320AA0": "ETU850",  # 250A
		"3VA21166KP320AA0": "ETU850",  # 160A
		"3VA21166KP320AA0": "ETU850",  # 160A
		"Micrologic 6.0X": "Micrologic 6.0X",  # 1000A for Shnieder MCCBs

	}

	with open(csv_breakers, mode='r', encoding='utf-8-sig') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
		for row in csv_reader:
			breaker_parameters = list()
			# check if row is not empty
			if len(row) < 17:
				continue

			circuit_number = re_circuit_number.search(row[0])
			if circuit_number:
				circuit_number = circuit_number.group(0)

			panel_name = re_panel_name.search(row[0])
			if panel_name:
				panel_name: str = panel_name.group(0)

			breaker_parameters.append(panel_name)
			breaker_parameters.append(circuit_number)

			# add trip parameter
			breaker_type = row[1]
			breaker_trip = breaker_trips.get(breaker_type)
			if not breaker_trip:
				breaker_trip = "-"

			breaker_parameters.append(breaker_trip)
			breaker_parameters.extend(row[2:5])
			breaker_parameters.extend(row[6:8])
			breaker_parameters.append(row[15])
			breaker_parameters += row[17:]
			breaker_parameters = [i.replace(",", "") if i else None for i in breaker_parameters]
			cbreakers_list.append(breaker_parameters)

	return cbreakers_list


def csv_to_rvt_elements(csv_info, doc):
	param_toset_circuits = [
		"_Breaker_Type",
		"RBS_ELEC_CIRCUIT_FRAME_PARAM",
		"_IR(LTPU)",
		"_tr(LTD)",
		"_Isd(STPU)",
		"_tsd(STD)",
		"_Ii(INST)",
		"_Ig(GFPU)",
		"_tg(GFD)"]
	param_toset_panel = [
		"_Breaker_Type",
		"RBS_ELEC_PANEL_MCB_RATING_PARAM",
		"_IR(LTPU)",
		"_tr(LTD)",
		"_Isd(STPU)",
		"_tsd(STD)",
		"_Ii(INST)",
		"_Ig(GFPU)",
		"_tg(GFD)"]

	elem_list = list()
	for row in csv_info:
		panel_name = row[0]
		if not panel_name:
			elem_list.append(None)
			continue

		circuit_number = int(row[1])
		panel_rvt = toolsrvt.inst_by_cat_strparamvalue(
			doc,
			BuiltInCategory.OST_ElectricalEquipment,
			BuiltInParameter.RBS_ELEC_PANEL_NAME,
			panel_name,
			False)
		# TODO: check if panel is not unique - write report
		# check panel name is equal to panel name
		try:
			panel_rvt = [i for i in panel_rvt if i.Name == panel_name][0]
		except:
			error_text = "Panel not found :" + panel_name
			raise ValueError(error_text)

		# "0" is main circuit breaker of the panel
		if circuit_number == 0:
			panels_list = [panel_rvt] * len(param_toset_panel)
			param_values = zip(panels_list, param_toset_panel, row[2:])
			elem_list.extend(param_values)

		# "%n" is branch circuit of the panel
		else:
			circutits_rvt = toolsrvt.elsys_by_brd(panel_rvt)[1]
			try:
				circutit_rvt = [i for i in circutits_rvt if i.StartSlot == circuit_number][0]
			except:
				# circuit in Simaris do not have analog in Revit model. Situation to be checked
				error_text = "Circuit not found :" + panel_name + ": " + str(circuit_number)
				raise ValueError(error_text)
			circutit_list = [circutit_rvt] * len(param_toset_circuits)
			# change value for frame to represent Revit value
			display_units = doc.GetUnits().GetFormatOptions(Autodesk.Revit.DB.SpecTypeId.Current).GetUnitTypeId()
			values_list = row[2:]
			values_list[1] = Autodesk.Revit.DB.UnitUtils.ConvertToInternalUnits(float(values_list[1]), display_units)

			param_values = zip(circutit_list, param_toset_circuits, values_list)
			elem_list.extend(param_values)

	return elem_list
