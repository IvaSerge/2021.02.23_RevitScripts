# imports rquired to install from pip
# pandas, Pillow, pip install -U pypiwin32
# pip install -U python-dotenv
# pip install mysql-connector-python

import clr
import os
import sys

dir_path = IN[0].DirectoryName  # type: ignore
sys.path.append(dir_path)

local_data = os.getenv("LOCALAPPDATA")

py_path = local_data + r"\python-3.9.12-embed-amd64\Lib\site-packages"
sys.path.append(py_path)

py_path = local_data + r"\python-3.9.12-embed-amd64\Lib\site-packages\win32"
sys.path.append(py_path)

py_path = local_data + r"\python-3.9.12-embed-amd64\Lib\site-packages\win32\lib"
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

from win32com import client

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
import db_reader
reload(db_reader)
from db_reader import *


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView
reload_var = IN[1]  # type: ignore
path_to_save = os.path.normpath(IN[2])  # type: ignore
manual_naming = IN[3]  # type: ignore
info_list = IN[4]  # type: ignore
filter_param_name = "BOQ Phase"  # filter parameter is hard coded

# get main BOQ parameters
if manual_naming:
	boq_name = info_list[0]  # type: ignore
	rev_doc_number = info_list[1]  # type: ignore
else:
	shop_code = info_list[0]
	discipline_code = info_list[1]
	# read DB adn get BOQ name and number automatically
	names_list = db_reader.get_boq_filename(
		dir_path,
		shop_code,
		discipline_code)
	boq_name = names_list[0]
	rev_doc_number = names_list[1]

rev_seq_number = info_list[2]  # type: ignore
filter_param_value = info_list[3]  # type: ignore

# get BOQ files to save
names_list = xl_writer.get_files_path(
	path_to_save,
	dir_path,
	boq_name,
	rev_doc_number,
	filter_param_value)

path_xlsx = names_list[0]
path_pdf = names_list[1]

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

boq_elems = list()
# Read parameters and organise data structure
# boq_inst = get_boq_by_elements(rvt_elems)
# boq_cables = get_boq_by_circuits(rvt_circuits)
# boq_trays = get_boq_by_tray(rvt_tray)
boq_fittings = get_boq_by_tray_fitting(rvt_tray_fitting)

# boq_elems.extend(boq_inst)
# boq_elems.extend(boq_cables)
# boq_elems.extend(boq_trays)
# boq_elems.extend(boq_trays)

# boq_elems_sorted = sorted_by_category(boq_elems)
# boq_with_header = add_headers(boq_elems_sorted)

# # Excel export
# xl_first_page = write_first_page(
# 	dir_path, path_xlsx, doc, boq_name, rev_seq_number,
# 	f'{rev_doc_number:02d}')
# xl_second_page = write_totals(path_xlsx, boq_with_header)

# # PDF export
# try:
# 	excel = client.Dispatch("Excel.Application")
# 	excel.Visible = False

# 	# Read Excel File
# 	wb = excel.Workbooks.Open(path_xlsx)
# 	wb.WorkSheets(["Cover", "BOQ Totals"]).Select()

# 	# Convert into PDF File
# 	wb.ActiveSheet.ExportAsFixedFormat(0, path_pdf)

# except Exception as e:
# 	raise ValueError(e)

# finally:
# 	wb.Close(False)
# 	excel.Quit()
# 	excel = None
	# wb = None

OUT = boq_fittings
