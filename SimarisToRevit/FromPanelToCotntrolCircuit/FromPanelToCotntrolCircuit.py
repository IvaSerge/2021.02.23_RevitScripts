"""
Read info in panel family instance and write to control circuit, if circuit exists
Main swich parameters are represented in this control circuit
"""
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

dir_path = IN[0].DirectoryName  # type: ignore
sys.path.append(dir_path)


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

import importlib
from importlib import reload

import csv
import re

# ================ local imports
import toolsrvt
reload(toolsrvt)
from toolsrvt import *


def get_parameters_from_panel(_el_sys):

	# check that it is correct circuit
	if _el_sys.Elements.Size == 1:
		panel = list(_el_sys.Elements)[0]
		doc = panel.Document
		panel_cat = category_by_bic_name(doc, "OST_ElectricalEquipment").Id
		if panel.Category.Id != panel_cat:
			# circuit contains no panels
			return None
	else:
		# not correct circuit
		return None

	param_toread_panel = [
		"_IR(LTPU)",
		"_tr(LTD)",
		"_Isd(STPU)",
		"_tsd(STD)",
		"_Ii(INST)",
		"_Ig(GFPU)",
		"_tg(GFD)"]

	el_sys_list = [_el_sys] * len(param_toread_panel)

	params_to_read = [toolsrvt.get_parval(panel, p_name) for p_name in param_toread_panel]
	params_to_set = zip(el_sys_list, param_toread_panel, params_to_read)

	return params_to_set


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView

reload_IN = IN[1]  # type: ignore
outlist = list()

# find all electrical circuits with SystemType == Controls
# in ElementSet find panel

el_systems = toolsrvt.inst_by_cat_strparamvalue(
	doc,
	BuiltInCategory.OST_ElectricalCircuit,
	BuiltInParameter.RBS_ELEC_CIRCUIT_TYPE,
	"Controls",
	False)

# read parameters from panel
# for el_sys in el_systems:
# 	sys_parameters = get_parameters_from_panel(el_sys)
get_parameters_from_panel(el_systems[0])

# ================ get info for circuit breaker settings


# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# ================ set parameters


# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = get_parameters_from_panel(el_systems[0])
