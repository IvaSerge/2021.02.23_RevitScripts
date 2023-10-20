
import clr
import sys
import os

import System
from System import Array
from System.Collections.Generic import *

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


class ExportDWG():

	@staticmethod
	def get_sheet_name(sheet):
		# start path is not importatn as printer driver uses it's default path
		sheet_name = toolsrvt.get_parval(sheet, "SHEET_NAME")
		sheet_number = toolsrvt.get_parval(sheet, "SHEET_NUMBER")
		revisions_list = ViewSheet.GetAllRevisionIds(sheet)
		if revisions_list:
			latest_revision = "[%s]" % str(len(revisions_list) - 1).zfill(2)
		else:
			latest_revision = ""

		pdf_name = sheet_number + "_DWG" + latest_revision
		pdf_name += " - " + sheet_name + ".dwg"

		return pdf_name

	@staticmethod
	def get_dwg_export_option(doc):
		# DWG export hard coded
		rvt_options = DWGExportOptions.GetPredefinedOptions(
			doc,
			"AutoCAD Exports")
		return rvt_options

	@staticmethod
	def export_view(rvt_sheet, export_path):
		doc = rvt_sheet.Document
		dwg_path = export_path + "\\DWG"
		if not os.path.isdir(dwg_path):
			os.mkdir(dwg_path)
		# dwg_name = dwg_path
		dwg_name = ExportDWG.get_sheet_name(rvt_sheet)

		dwg_list = List[ElementId]()  # Icollection for ElementId
		dwg_list.Add(rvt_sheet.Id)

		dwg_export_options = ExportDWG.get_dwg_export_option(doc)

		doc.Export(
			dwg_path,
			dwg_name,
			dwg_list,
			dwg_export_options
		)

		return dwg_name
