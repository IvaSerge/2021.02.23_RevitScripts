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

	with open(csv_breakers, mode='r') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
		for row in csv_reader:
			breaker_parameters = list()

			circuit_number = re_circuit_number.search(row[0])
			if circuit_number:
				circuit_number = circuit_number.group(0)

			panel_name = re_panel_name.search(row[0])
			if panel_name:
				panel_name: str = panel_name.group(0)

			breaker_parameters.append(panel_name)
			breaker_parameters.append(circuit_number)
			breaker_parameters += row[2:5]
			breaker_parameters += row[6:8]
			breaker_parameters += [row[15]]
			breaker_parameters += row[17:]

			# change "," "." for frame
			if "," in breaker_parameters[2]:
				breaker_parameters[2] = float(breaker_parameters[2].replace(",", ""))
			cbreakers_list.append(breaker_parameters)

	return cbreakers_list


def csv_to_rvt_elements(csv_info, doc):
	param_toset_circuits = [
		"RBS_ELEC_CIRCUIT_FRAME_PARAM",
		"_IR(LTPU)",
		"_tr(LTD)",
		"_Isd(STPU)",
		"_tsd(STD)",
		"_Ii(INST)",
		"_Ig(GFPU)",
		"_tg(GFD)"]
	param_toset_panel = [
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
		panel_rvt = [i for i in panel_rvt if i.Name == panel_name][0]

		# "0" is main circuit breaker of the panel
		if circuit_number == 0:
			panels_list = [panel_rvt] * len(param_toset_panel)
			param_values = zip(panels_list, param_toset_panel, row[2:])
			elem_list.extend(param_values)

		# "%n" is branch circuit of the panel
		else:
			circutit_rvt = toolsrvt.elsys_by_brd(panel_rvt)[1][circuit_number - 1]
			# check circuit is not a SPARE
			if circutit_rvt.CircuitType != Electrical.CircuitType.Circuit:
				# TODO add this circuit to error list
				continue

			circutit_list = [circutit_rvt] * len(param_toset_circuits)
			param_values = zip(circutit_list, param_toset_circuits, row[2:])
			elem_list.extend(param_values)

			# TODO: if circuit not found - write report
	return elem_list
