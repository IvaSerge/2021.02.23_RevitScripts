"""
tree_list_utils.py

A collection of utility functions for working with lists, including flatting lists,
create excel, write the list to excel and format the excel

Functions:
	flatten_with_none

"""

import clr
import os
import sys
import shutil


local_data = os.getenv("LOCALAPPDATA")
dyn_path = r"\python-3.9.12-embed-amd64\Lib"
py_path = local_data + dyn_path
sys.path.append(py_path)

# ================ Python imports
import openpyxl
import openpyxl.worksheet
import openpyxl.worksheet.header_footer
import openpyxl.worksheet.page


def flatten_with_none(in_list, level=0, result=None):
	"""Flattens a nested list while adding None for each new level, storing in global result."""
	result = []
	
	def inner(nested_list, level=0):
		nonlocal result
		for item in nested_list:
			# check inide list if it is any value
			# according to list structure, if first value is string -
			#  all list is a row and may be saved
			check_item = item[0]
			if isinstance(check_item, list):
				# recurcive search deeper
				inner(item, level + 1)
			else:
				row = [None] * level
				row.extend(item)
				result.append(row)

	inner(in_list)
	return result


def move_template_xls_file(dyn_path, xl_save_to):
	template_path = dyn_path + "\\boq_template.xlsx"
	shutil.copy(template_path, xl_save_to)


def create_file_name(panel_name, path_to_save):
	# xlsx file name
	name_xlsx = panel_name
	name_xlsx += ".xlsx"
	name_xlsx = path_to_save + "\\" + name_xlsx
	return name_xlsx