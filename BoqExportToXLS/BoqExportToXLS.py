# imports rquired to install from pip
# pandas, Pillow, pip install -U pypiwin32
# pip install -U python-dotenv
# pip install mysql-connector-python
# pip install openpyxl

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
shop_code = info_list[0]
discipline_code = info_list[1]
rev_seq_number = info_list[2]
rev_description = info_list[3]
filter_param_value = info_list[3]

# get main BOQ parameters
if manual_naming:
	boq_name = info_list[0]  # type: ignore
	rev_doc_number = info_list[1]  # type: ignore

else:
	# read DB adn get BOQ name and number automatically
	db_names = db_reader.get_db_boq_name_and_rev(
		dir_path,
		shop_code,
		discipline_code)
	boq_name = db_names[0]
	rev_doc_number = db_names[1]

# create path by name, revision and description
names_list = xl_writer.create_files_names(
	boq_name,
	rev_doc_number,
	rev_description,
	path_to_save)

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

# That is bad idea to add conduits, ducts, quasi-busbars and so on..
# Only standard cable trays to be calculated
bic_lenth_based_families = ["OST_CableTray"]
bic_fittings = ["OST_CableTrayFitting"]

rvt_elems = inst_by_multicategory_param_val(
	doc, bic_str_lst,
	filter_param_name,
	filter_param_value)

rvt_circuits = inst_by_multicategory_param_val(
	doc, ["OST_ElectricalCircuit"],
	filter_param_name,
	filter_param_value)

rvt_length_based_families = inst_by_multicategory_param_val(
	doc, bic_lenth_based_families,
	filter_param_name,
	filter_param_value)

rvt_fitting = inst_by_multicategory_param_val(
	doc, bic_fittings,
	filter_param_name,
	filter_param_value)

# Read parameters and organise data structure
boq_elems = list()
boq_inst = get_boq_by_elements(rvt_elems)
boq_cables = get_boq_by_circuits(rvt_circuits)
boq_l_based_families = get_boq_by_l_based_fam(rvt_length_based_families)
# boq_fittings = get_boq_by_fitting(rvt_fitting)

boq_elems.extend(boq_inst)
boq_elems.extend(boq_cables)
boq_elems.extend(boq_l_based_families)
# boq_elems.extend(boq_fittings)

boq_elems_sorted = sorted_by_category(boq_elems)
boq_with_header = add_headers(boq_elems_sorted)

# TODO: add effected drawings list

# Excel export
xl_first_page = write_first_page(
	dir_path, path_xlsx, doc, boq_name, rev_seq_number,
	f'{rev_doc_number:02d}')
xl_second_page = write_totals(path_xlsx, boq_with_header)

# # PDF export
# try:
# 	excel = client.Dispatch("Excel.Application")
# 	excel.Visible = False

# 	# Read Excel File
# 	wb = excel.Workbooks.Open(path_xlsx)
# 	wb.WorkSheets(["Cover", "General Notes", "BOQ Totals"]).Select()

# 	# Convert into PDF File
# 	wb.ActiveSheet.ExportAsFixedFormat(0, path_pdf)

# except Exception as e:
# 	raise ValueError(e)

# finally:
# 	wb.Close(False)
# 	excel.Quit()
# 	excel = None
# 	# wb = None

OUT = boq_elems
