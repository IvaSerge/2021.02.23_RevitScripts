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


def write_first_page(path, xl_name, doc, boq_name, seq_number):

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
	rev_number = "0"
	rev_description = revision.Description
	rev_issued_by = revision.IssuedBy

	# Cover page - write info
	xl_path = path + "\\boq_template.xlsx"
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

	# write to new path
	xl_path_new = path + "\\" + xl_name
	wb.save(xl_path_new)

	return xl_path_new


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
