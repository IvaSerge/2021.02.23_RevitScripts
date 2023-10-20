import clr

import sys

dir_path = IN[0].DirectoryName  # type: ignore
sys.path.append(dir_path)


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
import json

# ================ local imports
import toolsrvt
reload(toolsrvt)
from toolsrvt import *
import print_view
reload(print_view)
from print_view import PrintView
import dwg_export
reload(dwg_export)
from dwg_export import ExportDWG


def get_sheet_by_revision_number(doc, seq_number):
	revisions = FilteredElementCollector(doc).\
		OfClass(Autodesk.Revit.DB.Revision).ToElements()
	revision_id = [i.Id for i in revisions if i.SequenceNumber == seq_number]

	if not revision_id:
		raise ValueError("Revision not found")
	else:
		revision_id = revision_id[0]

	all_sheets = FilteredElementCollector(doc).\
		OfCategory(BuiltInCategory.OST_Sheets).\
		WhereElementIsNotElementType().\
		ToElements()

	rvt_sheets = list()
	for sheet in all_sheets:
		revisions_on_sheet = ViewSheet.GetAllRevisionIds(sheet)
		if revision_id in revisions_on_sheet:
			rvt_sheets.append(sheet)

	return rvt_sheets


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView
reload_var = IN[1]  # type: ignore
printer_name = IN[2]  # type: ignore
print_default_path = IN[3]  # type: ignore
print_save_path = IN[4]  # type: ignore
to_print_sheets = IN[5]  # type: ignore

sheets_list = list()

if isinstance(to_print_sheets, list):
	# remove duplicates
	to_print_sheets = set(to_print_sheets)
	for sheet_number in to_print_sheets:
		rvt_sheet = toolsrvt.inst_by_cat_strparamvalue(
			doc,
			BuiltInCategory.OST_Sheets,
			BuiltInParameter.SHEET_NUMBER,
			sheet_number,
			False)
		if rvt_sheet:
			sheets_list.append(rvt_sheet[0])
elif isinstance(to_print_sheets, int):
	sheets_list = get_sheet_by_revision_number(doc, to_print_sheets)
else:
	error_text = "Wrong input parameters"
	raise ValueError(error_text)

if not sheets_list:
	error_text = "Sheets to print not found"
	raise ValueError(error_text)

TransactionManager.Instance.EnsureInTransaction(doc)

view_sets = FilteredElementCollector(doc).OfClass(ViewSheetSet)
for i in view_sets:
	if i.Name == "tempSetName":
		doc.Delete(i.Id)

for rvt_sheet in sheets_list:
	PrintView.print_view(rvt_sheet, printer_name, dir_path)
	ExportDWG.export_view(rvt_sheet, print_save_path)

TransactionManager.Instance.TransactionTaskDone()

OUT = sheets_list
