import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
sys.path.append(IN[0].DirectoryName)  # type: ignore

clr.AddReferenceByName('Microsoft.Office.Interop.Excel, Version=11.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c')
from Microsoft.Office.Interop import Excel  # type: ignore

import System
from System import Array
from System.Collections.Generic import *

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager


import presets
from presets import *


def GetParVal(elem, name):
	value = None
	# custom parameter
	param = elem.LookupParameter(name)
	# check is it a BuiltIn parameter if not found
	if not(param):
		param = elem.get_Parameter(GetBuiltInParam(name))

	# get paremeter Value if found
	try:
		storeType = param.StorageType
		# value = storeType
		if storeType == StorageType.String:
			value = param.AsString()
		elif storeType == StorageType.Integer:
			value = param.AsDouble()
		elif storeType == StorageType.Double:
			value = param.AsDouble()
		elif storeType == StorageType.ElementId:
			value = param.AsValueString()
	except:
		pass
	return value


def GetBuiltInParam(paramName):
	builtInParams = System.Enum.GetValues(BuiltInParameter)
	param = []
	for i in builtInParams:
		if i.ToString() == paramName:
			param.append(i)
			return i


def getSystems(_brd):
	"""Get all systems of electrical board.

		args:
		_brd - electrical board FamilyInstance

		return list(1, 2) where:
		1 - main electrical circuit
		2 - list of connectet low circuits
	"""
	allsys = _brd.MEPModel.GetElectricalSystems()
	lowsys = _brd.MEPModel.GetAssignedElectricalSystems()
	if lowsys:
		lowsysId = [i.Id for i in lowsys]
		mainboardsysLst = [i for i in allsys if i.Id not in lowsysId]
		if len(mainboardsysLst) == 0:
			mainboardsys = None
		else:
			mainboardsys = mainboardsysLst[0]
		lowsys = [i for i in allsys if i.Id in lowsysId]
		lowsys.sort(key=lambda x: x.CircuitNumber)
		return mainboardsys, lowsys
	else:
		return [i for i in allsys][0], None


global doc
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application

reload = IN[1]  # type: ignore

# get FamilyInstance of the board, that need to be converted
board_to_convert = UnwrapElement(IN[2])  # type: ignore

# get preset
if not(IN[3]):  # type: ignore
	raise ValueError("No preset found")
elif "3A_sub" == IN[3]:  # type: ignore
	user_preset = presets.preset_3A_sub
elif "3B_sub" == IN[3]:  # type: ignore
	user_preset = presets.preset_3B_sub
elif "2E_main" == IN[3]:  # type: ignore
	user_preset = presets.preset_2E_main
elif "2E_sub" == IN[3]:  # type: ignore
	user_preset = presets.preset_2E_sub
elif "2E1_main" == IN[3]:  # type: ignore
	user_preset = presets.preset_2E1_main
elif "2E1_sub" == IN[3]:  # type: ignore
	user_preset = presets.preset_2E1_sub
elif "2H" == IN[3]:  # type: ignore
	user_preset = presets.preset_2H
elif "2I" == IN[3]:  # type: ignore
	user_preset = presets.preset_2I
elif "2J_main" == IN[3]:  # type: ignore
	user_preset = presets.preset_2J_main
elif "2J_sub" == IN[3]:  # type: ignore
	user_preset = presets.preset_2J_sub
elif "2R_main" == IN[3]:  # type: ignore
	user_preset = presets.preset_2R_main
elif "2R_sub" == IN[3]:  # type: ignore
	user_preset = presets.preset_2R_sub
elif "2R2_main" == IN[3]:  # type: ignore
	user_preset = presets.preset_2R2_main
elif "2R2_sub" == IN[3]:  # type: ignore
	user_preset = presets.preset_2R2_sub
elif "2S_main" == IN[3]:  # type: ignore
	user_preset = presets.preset_2S_main
elif "2S_sub" == IN[3]:  # type: ignore
	user_preset = presets.preset_2S_sub
elif "2T_main" == IN[3]:  # type: ignore
	user_preset = presets.preset_2T_main
elif "2U_main" == IN[3]:  # type: ignore
	user_preset = presets.preset_2U_main
elif "2U_sub" == IN[3]:  # type: ignore
	user_preset = presets.preset_2U_sub

# get PanelScheduleView if no view found - create Default
board_schedule = [x for x in FilteredElementCollector(doc).
	OfClass(Autodesk.Revit.DB.Electrical.PanelScheduleView).
	ToElements()
	if x.TargetId == board_to_convert.Id]
if board_schedule:
	board_schedule = board_schedule[0]  # type: Autodesk.Revit.DB.Electrical.PanelScheduleView


# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# TODO: CHECK IF THE SCHEDULE IS EMPTY!

options_list = user_preset[1]
options_column = user_preset[0]

for i, option in enumerate(options_list, start=2):
	# in view create Spare
	try:
		board_schedule.AddSpare(i, 1)
	except:
		continue
	# Set options to columns
	for column, opt_to_set in zip(options_column, option):
		board_schedule.SetParamValue(SectionType.Body, i, column, opt_to_set)
	doc.Regenerate()


# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = options_list, options_column
