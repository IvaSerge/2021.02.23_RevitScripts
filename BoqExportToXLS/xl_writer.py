import clr
import os
import sys

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
import openpyxl

from PIL import Image

# ================ local imports
import toolsrvt
reload(toolsrvt)
from toolsrvt import *
import db_reader
reload(db_reader)
from db_reader import *


def check_file_name(file_name):

	for char in file_name:
		if char in "<:\"/\\|?*":
			raise ValueError("Wrong file name")
	if len(file_name) > 80:
		raise ValueError("File name is too long")

	return True


def get_file_manualy(path_to_save, dir_path, boq_name, rev_doc_number, filter_param_value):

	# Check revision in database
	name_list = get_info_by_name(dir_path, boq_name, rev_doc_number, filter_param_value)

	name_xlsx = name_list[0]
	name_pdf = name_list[1]
	path_xlsx = path_to_save + "\\" + name_xlsx
	path_pdf = path_to_save + "\\" + name_pdf
	check_file_name(name_xlsx)
	check_file_name(name_pdf)

	return path_xlsx, path_pdf


def write_first_page(dyn_path, xl_save_to, doc, boq_name, seq_number, rev_number):

	# get project info
	proj_status = doc.ProjectInformation.Status
	proj_address = doc.ProjectInformation.Address

	# project Discipline is project specific
	proj_discipline = doc.ProjectInformation.LookupParameter("Discipline")
	if proj_discipline:
		proj_discipline = doc.ProjectInformation.LookupParameter("Discipline").AsString()
	elif doc.ProjectInformation.LookupParameter("TSLA_ProjectDiscipline"):
		proj_discipline = doc.ProjectInformation.LookupParameter("TSLA_ProjectDiscipline").AsString()
	else:
		raise ValueError("Project Dyscipline not found")

	proj_str = proj_status + ". "
	proj_str += proj_address + ". "
	proj_str += proj_discipline

	# get revision info
	revisions = FilteredElementCollector(doc).\
		OfClass(Autodesk.Revit.DB.Revision).ToElements()
	revision = [i for i in revisions if i.SequenceNumber == seq_number]

	if not revision:
		raise ValueError("Revision not found")
	else:
		revision = revision[0]

	rev_date = revision.RevisionDate
	rev_description = revision.Description
	rev_issued_by = revision.IssuedBy

	# Cover page - write info
	xl_path = dyn_path + "\\boq_template.xlsx"
	wb = openpyxl.load_workbook(xl_path)
	wb.active = wb["Cover"]
	ws = wb.active

	ws["A32"] = proj_str
	ws["A34"] = boq_name
	ws["A44"] = rev_date
	ws["B44"] = rev_number
	ws["C44"] = rev_description
	ws["H44"] = rev_issued_by

	# check cell height based on revision description
	# max str length is 47
	rev_description_height = math.ceil(
		len(rev_description) / 47)
	ws.row_dimensions[44].height = 15.75 * rev_description_height

	# save to new path
	wb.save(xl_save_to)

	return xl_save_to


def write_totals(xl_path, totals_lst):

	# Second page - write info
	wb = openpyxl.load_workbook(xl_path)
	wb.active = wb["BOQ Totals"]
	ws: openpyxl.Workbook.worksheets = wb.active

	# set columns width
	ws.column_dimensions["A"].width = 62
	ws.column_dimensions["B"].width = 10
	ws.column_dimensions["C"].width = 24

	rw = 1
	for category in totals_lst:
		rw += 1
		for r_count, row in enumerate(category, 1):
			for clmn, val in enumerate(row, 1):
				current_cell = ws.cell(row=rw, column=clmn)

				# get and set cell style by row
				if r_count == 1:
					# first line
					style_cell = "DiRootsFullNameTitleStyle"

				elif r_count == 2:
					# second line
					style_cell = "DiRootsHeaderStyle"

				else:
					# other lines
					style_cell = "Normal"

				current_cell.style = style_cell
				if val:
					current_cell.value = val
			rw += 1

	# set print area
	first_cell = "A1"
	last_cell = ws.cell(row=rw, column=3).coordinate
	ws.print_area = first_cell + ":" + last_cell

	wb.save(xl_path)
	return True
