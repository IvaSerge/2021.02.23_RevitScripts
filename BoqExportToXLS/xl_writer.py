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
from math import ceil

# ================ local imports
import toolsrvt
reload(toolsrvt)
from toolsrvt import *


def write_first_page(path, doc, boq_name, seq_number):

	# get project info
	proj_status = doc.ProjectInformation.Status
	proj_address = doc.ProjectInformation.Address
	proj_discipline = doc.ProjectInformation.LookupParameter("Discipline").AsString()

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

	ws["A47"] = rev_date
	ws["B47"] = rev_number
	ws["C47"] = rev_description
	ws["H47"] = rev_issued_by

	# check cell height based on revision description
	# max str length is 42
	rev_description_height = math.ceil(
		len(rev_description) / 42)
	ws.row_dimensions[47].height = 15.75 * rev_description_height

	wb.save(xl_path)

	return rev_description_height


def sorted_by_category(list_of_lists):
	"""Groups list by category where:\\
		key is list[0], values are list[1:]
	"""
	result_dict = dict()

	for lst in list_of_lists:
		if not result_dict.get(lst[0]):
			# new value
			result_dict.update({lst[0]: [lst[1:]]})

		else:
			# value exists
			current_val = [i for i in result_dict.get(lst[0])] + ([lst[1:]])
			result_dict.update({lst[0]: current_val})

	return sorted(list(result_dict.items()), key=lambda x: x[0])


def write_totals(boq_totals):
	# sort totals by category
	boq_sorted = sorted_by_category(boq_totals)

	# for every category create empty row, row with category Name
	# change font and colour

	# add all data

	# set cell borders

	return boq_sorted
