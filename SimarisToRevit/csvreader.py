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
	re_circuit_number = re.compile(r"(?<=\[)*.(?=\])")
	re_panel_name = re.compile(r".+(?=\[)")

	with open(csv_breakers, mode='r') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=';', quoting=csv.QUOTE_MINIMAL)
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
			breaker_parameters += row[1:5]
			breaker_parameters += row[6:8]
			breaker_parameters += [row[15]]
			breaker_parameters += row[17:]

			cbreakers_list.append(breaker_parameters)

	return cbreakers_list


def csv_to_rvt_elements(csv_info, doc):
	param_toset_cb = [
		"_Breaker_Type",
		"RBS_ELEC_CIRCUIT_FRAME_PARAM",
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
		if circuit_number == 0:
			panel_rvt = toolsrvt.inst_by_cat_strparamvalue(
				doc,
				BuiltInCategory.OST_ElectricalEquipment,
				BuiltInParameter.RBS_ELEC_PANEL_NAME,
				panel_name,
				False)
			# check panel name is equal to panel name
			panel_rvt = [i for i in panel_rvt if i.Name == panel_name][0]
			panels_list = [panel_rvt] * len(param_toset_cb)
			param_values = zip(panels_list, param_toset_cb, row[2:])
			elem_list.append(param_values)
	return elem_list
