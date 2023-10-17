
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


class PrintView():

	def __init__(self, rvt_sheet, printer_name):
		doc = rvt_sheet.Document
		print_range = PrintRange.Select
		print_combine = False

		# TODO: get setting automaticaly by title on the sheet
		print_settings = FilteredElementCollector(doc).\
			OfClass(PrintSetting).ToElements()[1]

		print_manager = doc.PrintManager
		print_manager.PrintRange = print_range
		print_manager.Apply()

		view_set = ViewSet()
		view_set.Insert(rvt_sheet)

		# make new view set current
		view_setting = print_manager.ViewSheetSetting
		view_setting.CurrentViewSheetSet.Views = view_set

		# set printer
		print_manager.SelectNewPrintDriver(printer_name)
		print_manager.Apply()

		# set combined and print to file
		print_manager.CombinedFile = False
		print_manager.Apply()
		print_manager.PrintToFile = True
		print_manager.Apply()

		TransactionManager.Instance.EnsureInTransaction(doc)
		view_setting.SaveAs("tempSetName")
		print_manager.Apply()
		print_manager.SubmitPrint()
		view_setting.Delete()
		TransactionManager.Instance.TransactionTaskDone()

	def move_to_path(path_str):
		# TODO: move file to path
		pass

	def size_by_title_block(sheet):
		# TODO: find title block and get size of it
		pass
