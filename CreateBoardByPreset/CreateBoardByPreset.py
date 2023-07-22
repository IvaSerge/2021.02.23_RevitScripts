import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
sys.path.append(IN[0].DirectoryName)  # type: ignore

dir_path = IN[0].DirectoryName  # type: ignore
sys.path.append(dir_path)

import System
from System import Array
from System.Collections.Generic import *

# ================ Revit imports
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager


import importlib
from importlib import reload

import json

import toolsrvt
reload(toolsrvt)

import itertools
from itertools import cycle


def create_spares(board_to_convert, user_preset):
	# get PanelScheduleView if no view found - create Default
	board_schedule = [x for x in FilteredElementCollector(doc).
		OfClass(Autodesk.Revit.DB.Electrical.PanelScheduleView).
		ToElements()
		if x.TargetId == board_to_convert.Id]
	if board_schedule:
		board_schedule = board_schedule[0]  # type: Autodesk.Revit.DB.Electrical.PanelScheduleView

	for i, values in enumerate(user_preset, start=2):
		# in view create Spare
		try:
			board_schedule.AddSpare(i, 1)
		except:
			continue

		# Set parameters
		circuit_spare = board_schedule.GetCircuitByCell(i, 1)
		params_to_set = zip(
			cycle([circuit_spare]),
			data["spare_parameter_names"],
			values)

		for param_info in params_to_set:
			elem = param_info[0]
			p_name = param_info[1]
			p_value = param_info[2]
			toolsrvt.setup_param_value(elem, p_name, p_value)

		doc.Regenerate()


global doc
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application

reload = IN[1]  # type: ignore

# get FamilyInstance of the board, that need to be converted
board_ref = uidoc.Selection.PickObject(
	Autodesk.Revit.UI.Selection.ObjectType.Element,
	"Select panel")

board_to_convert = doc.GetElement(board_ref.ElementId)

# read JSON
json_file = dir_path + "\\" + "db_panels.json"
with open(json_file, "r") as f_db:
		data = json.load(f_db)

try:
	test_preset = user_preset = data["panel_types"][IN[2]]  # type: ignore
except:
	error_text = "Preset " + IN[2] + " not found"  # type: ignore
	raise ValueError(error_text)


user_preset = data["panel_types"][IN[2]]["spare_parameter_values"]  # type: ignore
board_parameters = data["panel_types"][IN[2]]["panel_parameter_values"]  # type: ignore

with Autodesk.Revit.DB.Transaction(doc, "CreateBoardByPreset") as t:
	# =========Start transaction
	t.Start()

	create_spares(board_to_convert, user_preset)

	# set panel parameters
	for param_info in board_parameters:
		elem = board_to_convert
		p_name = param_info[0]
		p_value = param_info[1]
		toolsrvt.setup_param_value(elem, p_name, p_value)

	t.Commit()

OUT = board_to_convert
