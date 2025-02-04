"""
tree_list_utils.py

A collection of utility functions for working with lists, including flatting lists,
create excel, write the list to excel and format the excel

Functions:
	flatten_with_none
	create_new_xlsx
	create_file_name
	write_totals
"""

__all__ = [
	"flatten_with_none",
	"create_new_xlsx",
	"create_file_name",
	"write_totals"
]

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
				inner(item, level + 2)
			else:
				row = [None] * level
				row.extend(item)
				result.append(row)

	inner(in_list)
	return result


def create_new_xlsx(temp_path, xl_save_to):
	shutil.copy(temp_path, xl_save_to)


def create_file_name(panel_name, path_to_save):
	# xlsx file name
	name_xlsx = panel_name
	name_xlsx += ".xlsx"
	name_xlsx = path_to_save + "\\" + name_xlsx
	return name_xlsx


def write_totals(xl_path, info_to_set):
	wb = openpyxl.load_workbook(xl_path)
	ws = wb["Panel_tree"]
	wb.active = wb["Panel_tree"]

	for rw, row in enumerate(info_to_set,1):
		# save info
		for clmn, val in enumerate(row, 1):
			current_cell = ws.cell(row=rw, column=clmn)
			if val:
				current_cell.value = val
	
	# format columns
	# odd column - circit breaker N. - narrow
	# even column - circuit name - wide
	for col in range(1, ws.max_column + 1):
		column_letter = ws.cell(row=1, column=col).column_letter  # Get column letter
		if col % 2 == 0:  # Even column
			ws.column_dimensions[column_letter].width = 20
		else:  # Odd column
			ws.column_dimensions[column_letter].width = 5
	wb.save(xl_path)