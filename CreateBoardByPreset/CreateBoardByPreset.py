import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
sys.path.append(IN[0].DirectoryName)  # type: ignore

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

import presets
reload(presets)
from presets import *

import toolsrvt
reload(toolsrvt)

import board_params
reload(board_params)

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
			presets.parameters_to_set,
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

# get preset
if not IN[2]:  # type: ignore
	raise ValueError("No preset found")
elif "3A_sub" == IN[2]:  # type: ignore
	user_preset = presets.preset_3A_sub
	board_parameters = board_params.preset_3A_sub
elif "3B_sub" == IN[2]:  # type: ignore
	user_preset = presets.preset_3B_sub
	board_parameters = board_params.preset_3B_sub
elif "2A" == IN[2]:  # type: ignore
	user_preset = presets.preset_2A
	board_parameters = board_params.preset_2A
elif "2C" == IN[2]:  # type: ignore
	user_preset = presets.preset_2C
	board_parameters = board_params.preset_2C
elif "2E_main" == IN[2]:  # type: ignore
	user_preset = presets.preset_2E_main
	board_parameters = board_params.preset_2E_main
elif "2E_sub" == IN[2]:  # type: ignore
	user_preset = presets.preset_2E_sub
	board_parameters = board_params.preset_2E_sub
elif "2E1_main" == IN[2]:  # type: ignore
	user_preset = presets.preset_2E1_main
	board_parameters = board_params.preset_2E1_main
elif "2E1_sub" == IN[2]:  # type: ignore
	user_preset = presets.preset_2E1_sub
	board_parameters = board_params.preset_2E1_sub
elif "2H" == IN[2]:  # type: ignore
	user_preset = presets.preset_2H
	board_parameters = board_params.preset_2H
elif "2I" == IN[2]:  # type: ignore
	user_preset = presets.preset_2I
	board_parameters = board_params.preset_2I
elif "2J_main" == IN[2]:  # type: ignore
	user_preset = presets.preset_2J_main
	board_parameters = board_params.preset_2J_main
elif "2J_sub" == IN[2]:  # type: ignore
	user_preset = presets.preset_2J_sub
	board_parameters = board_params.preset_2J_sub
elif "2R_main" == IN[2]:  # type: ignore
	user_preset = presets.preset_2R_main
	board_parameters = board_params.preset_2R_main
elif "2R_sub" == IN[2]:  # type: ignore
	user_preset = presets.preset_2R_sub
	board_parameters = board_params.preset_2R_sub
elif "2R2_main" == IN[2]:  # type: ignore
	user_preset = presets.preset_2R2_main
	board_parameters = board_params.preset_2R2_main
elif "2R2_sub" == IN[2]:  # type: ignore
	user_preset = presets.preset_2R2_sub
	board_parameters = board_params.preset_2R2_sub
elif "2S_main" == IN[2]:  # type: ignore
	user_preset = presets.preset_2S_main
	board_parameters = board_params.preset_2S_main
elif "2S_sub" == IN[2]:  # type: ignore
	user_preset = presets.preset_2S_sub
	board_parameters = board_params.preset_2S_sub
elif "2T_main" == IN[2]:  # type: ignore
	user_preset = presets.preset_2T_main
	board_parameters = board_params.preset_2T_main
elif "2T_sub" == IN[2]:  # type: ignore
	user_preset = presets.preset_2T_sub
	board_parameters = board_params.preset_2T_sub
elif "2U_main" == IN[2]:  # type: ignore
	user_preset = presets.preset_2U_main
	board_parameters = board_params.preset_2U_main
elif "2U_sub" == IN[2]:  # type: ignore
	user_preset = presets.preset_2U_sub
	board_parameters = board_params.preset_2U_sub

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
# OUT = board_schedule
