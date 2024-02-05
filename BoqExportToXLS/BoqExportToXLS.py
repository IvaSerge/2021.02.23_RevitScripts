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
import rvt_obj_group
reload(rvt_obj_group)
from rvt_obj_group import *

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
	rev_doc_number = f"{int(info_list[1]):02d}"

else:
	# read DB adn get BOQ name and number automatically
	db_names = db_reader.get_db_boq_name_and_rev(
		dir_path,
		shop_code,
		discipline_code)
	boq_name = db_names[0]
	rev_doc_number = db_names[1]


# # create path by name, revision and description
names_list = xl_writer.create_files_names(
	boq_name,
	rev_doc_number,
	rev_description,
	path_to_save)

path_xlsx = names_list[0]
path_pdf = names_list[1]

RvtObjGroup.doc = doc
RvtObjGroup.boq_parameter = filter_param_name
RvtObjGroup.boq_param_value = filter_param_value

boq_list = []

elec_bic_list = (
	"OST_ConduitFitting",
	"OST_DataDevices",
	"OST_ElectricalEquipment",
	"OST_ElectricalFixtures",
	"OST_FireAlarmDevices",
	"OST_GenericModel",
	"OST_LightingDevices",
	"OST_LightingFixtures",
	"OST_NurseCallDevices")
boq_electrical = sorted([electrical_objects(i) for i in elec_bic_list])
boq_electrical = [electrical_objects(i) for i in elec_bic_list]
boq_list.extend(boq_electrical)

boq_cables = electrical_circuits()
boq_list.append(boq_cables)

# TODO: maybe it is worth to filter cable trays inside script
boq_trays = tsla_trays()
boq_list.append(boq_trays)

# rvt_length_based_families = inst_by_multicategory_param_val(
# 	doc, bic_lenth_based_families,
# 	filter_param_name,
# 	filter_param_value)

boq_list = [i for i in boq_list if i.boq]
# TODO: add fittings boq. Standard fittign to be filtered correctly
# TODO: add effected drawings list

# Excel export
move_template_xls_file(dir_path, path_xlsx)
write_first_page(
	path_xlsx,
	boq_name, rev_doc_number,
	rev_seq_number,
	doc)
write_totals(path_xlsx, boq_list)

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

OUT = boq_list
