import clr
import os
import sys

dir_path = IN[0].DirectoryName  # type: ignore
sys.path.append(dir_path)

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
import boq_analyze
reload(boq_analyze)
from boq_analyze import *
import xl_writer
reload(xl_writer)
from xl_writer import *


def check_path_name(file_path):
	for char in file_path:
		if char in "<:\"/\\|?*":
			raise ValueError("Wrong file name")

	if len(name_xlsx) > 80:
		raise ValueError("File name is too long")

	return True


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView
reload_var = IN[1]  # type: ignore
boq_name = IN[2]  # type: ignore
rev_number = IN[3]  # type: ignore
filter_param_value = IN[4]  # type: ignore
filter_param_name = "BOQ Phase"  # filter parameter is hard coded

# Get all instances by DCN number of different categories
bic_str_lst = (
	"OST_ConduitFitting",
	"OST_DataDevices",
	"OST_ElectricalEquipment",
	"OST_ElectricalFixtures",
	"OST_FireAlarmDevices",
	"OST_GenericModel",
	"OST_LightingDevices",
	"OST_LightingFixtures",
	"OST_NurseCallDevices",
	"OST_SecurityDevices")


rvt_elems = inst_by_multicategory_param_val(
	doc, bic_str_lst,
	filter_param_name,
	filter_param_value)

rvt_circuits = inst_by_multicategory_param_val(
	doc, ["OST_ElectricalCircuit"],
	filter_param_name,
	filter_param_value)

rvt_tray = inst_by_multicategory_param_val(
	doc, ["OST_CableTray"],
	filter_param_name,
	filter_param_value)

rvt_tray_fitting = inst_by_multicategory_param_val(
	doc, ["OST_CableTrayFitting"],
	filter_param_name,
	filter_param_value)


# TODO read databaase for check revision and name
name_number = IN[2]
name_prefix = "_XLSX"
name_rev = "[00]"
name_description = IN[4]  # type: ignore

name_xlsx = name_number
name_xlsx += name_prefix + name_rev
name_xlsx += " - BOQ - " + name_description
name_xlsx += ".xlsx"

check_path_name(name_xlsx)


# Read parameters and organise data structure
boq_elems: list = get_boq_by_elements(rvt_elems)
boq_cables = get_boq_by_circuits(rvt_circuits)
# TODO: boq for cable trays and fittings

boq_elems.extend(boq_cables)
boq_elems_sorted = sorted_by_category(boq_elems)
boq_with_header = add_headers(boq_elems_sorted)

# Excel export
xl_first_page = write_first_page(dir_path, name_xlsx, doc, boq_name, rev_number)
xl_second_page = write_totals(xl_first_page, boq_with_header)

# PDF export
# TODO PDF export using com.32
# from win32com import client

# # Open Microsoft Excel
# excel = client.Dispatch("Excel.Application")

# # Read Excel File
# sheets = excel.Workbooks.Open('Excel File Path')
# work_sheets = sheets.Worksheets[0]

# # Convert into PDF File
# work_sheets.ExportAsFixedFormat(0, 'PDF File Path')

OUT = xl_first_page
