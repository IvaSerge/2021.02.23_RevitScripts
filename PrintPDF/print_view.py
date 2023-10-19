
import clr
import sys
import json

# ================ Revit imports
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# ================ local imports
import toolsrvt


class PrintView():

	def move_to_path(path_str):
		# TODO: move file to path
		pass

	def size_by_title_block(sheet):
		# TODO: find title block and get size of it
		pass

	@staticmethod
	def get_sheet_name(sheet):
		# start path is not importatn as printer driver uses it's default path
		start_path = "C:\\"
		sheet_name = toolsrvt.get_parval(sheet, "SHEET_NAME")
		sheet_number = toolsrvt.get_parval(sheet, "SHEET_NUMBER")
		revisions_list = ViewSheet.GetAllRevisionIds(sheet)
		if revisions_list:
			latest_revision = "[%s]" % str(len(revisions_list) - 1).zfill(2)
		else:
			latest_revision = ""

		pdf_name = start_path + sheet_number + latest_revision
		pdf_name += " - " + sheet_name + ".pdf"

		return pdf_name

	@staticmethod
	def get_print_setting_by_sheet(rvt_sheet, dir_path):

		doc = rvt_sheet.Document
		json_file = dir_path + "\\" + "db_sheet_settings.json"
		with open(json_file, "r") as f_db:
			data = json.load(f_db)

		# find title block
		title_blocks = FilteredElementCollector(doc, rvt_sheet.Id).\
			OfCategory(BuiltInCategory.OST_TitleBlocks).ToElements()

		if not title_blocks:
			error_str = "No title block on the %s sheet found" % rvt_sheet.SheetNumber
			raise ValueError(error_str)

		# get setting name from json by title block
		for t_block in title_blocks:
			t_block_type = toolsrvt.get_parval(t_block.Symbol, "ALL_MODEL_TYPE_NAME")
			t_block_family = toolsrvt.get_parval(t_block.Symbol, "ALL_MODEL_FAMILY_NAME")

			db_family = data.get(t_block_family)
			if db_family:
				setting_name = db_family.get(t_block_type)
				if setting_name:
					break
			else:
				continue

		if not setting_name:
			error_str = "print setting not in data base"
			raise ValueError(error_str)

		print_settings = FilteredElementCollector(doc).\
			OfClass(PrintSetting).ToElements()

		rvt_print_setting = [i for i in print_settings if i.Name == setting_name]
		if rvt_print_setting:
			rvt_print_setting = rvt_print_setting[0]
		else:
			error_str = "print setting \"%s\" not in Revit not found" % setting_name
			raise ValueError(error_str)

		return rvt_print_setting

	@staticmethod
	def print_view(rvt_sheet, printer_name, script_path):
		doc = rvt_sheet.Document

		sheet_name = PrintView.get_sheet_name(rvt_sheet)
		print_range = PrintRange.Select

		print_settings = PrintView.get_print_setting_by_sheet(rvt_sheet, script_path)
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
		print_manager.CombinedFile = True
		print_manager.Apply()
		print_manager.PrintToFile = True
		print_manager.Apply()
		print_manager.PrintToFileName = sheet_name
		print_manager.Apply()

		# # view settings
		print_setup = print_manager.PrintSetup
		print_setup.CurrentPrintSetting = print_settings
		# print_current_settings = print_setup.CurrentPrintSetting
		# print_current_settings = print_settings
		# print_current_settings = print_manager.PrintSetup.InSession
		# print_current_settings.PrintParameters.ZoomType = ZoomType.Zoom
		# print_current_settings.PrintParameters.Zoom = 100
		# print_current_settings.PageOrientation = PageOrientationType.Landscape
		# papeer_size = print_settings.PrintParameters.PaperSize
		print_manager.Apply()

		view_sets = FilteredElementCollector(doc).OfClass(ViewSheetSet)
		for i in view_sets:
			if i.Name == "tempSetName":
				doc.Delete(i.Id)

		view_setting.SaveAs("tempSetName")
		print_manager.Apply()
		print_manager.SubmitPrint()
		view_setting.Delete()
