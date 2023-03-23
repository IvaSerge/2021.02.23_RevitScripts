from operator import indexOf
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
sys.path.append(IN[0].DirectoryName)  # type: ignore

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

global doc
doc = DocumentManager.Instance.CurrentDBDocument


class Panel():
	# sheet-panel relation list [[sheet, "Location1,Location2"]]
	sheet_panel_list = list()

	"""A class to represent Revit panel"""
	def __init__(self, rvt_panel):
		# type: (Panel, FamilyInstance) -> None
		"""Create Panel by Revit panel FamilyInstance
		args:
			net_name (str):
		"""
		self.instances = rvt_panel
		self.panel_name = rvt_panel.Name
		self.on_sheets = self.find_related_sheet()
		self.location = self.get_location()

	def find_related_sheet(self):
		global sheets_list
		return_list = list()
		for sheet in sheets_list:
			if self.panel_name in sheet.Name:
				return_list.append(sheet)
		return return_list

	def get_location(self):
		params = self.instances.GetParameters("TSLA_SCOPE_ID")
		for param in params:
			if param.Id.IntegerValue == 7955181:
				return param.AsString()

	def add_info_to_list(self):

		# if location do not exist, no action.
		if not self.location:
			return None

		sheets_existing = [i[0] for i in Panel.sheet_panel_list if Panel.sheet_panel_list]
		sheets_to_add = self.on_sheets

		# check if current sheets are allready in the list
		if sheets_existing:
			sheets_existing_names = [i.Name for i in sheets_existing]
		else:
			sheets_existing_names = None

		out_list = list()
		for sheet in sheets_to_add:
			# if sheet exists in the list allready
			# if exists - get the sheet index
			if sheets_existing_names and sheet.Name in sheets_existing_names:
				sheet_index = sheets_existing_names.index(sheet.Name)
			else:
				sheet_index = None

			# location to be add to existing schedule
			if sheet_index is not None:
				current_location = Panel.sheet_panel_list[sheet_index][1]
				if self.location not in current_location:
					current_location = current_location + "," + self.location
					Panel.sheet_panel_list[sheet_index][1] = current_location
					out_list.append([sheet, current_location])

			# location to append to shedule
			else:
				Panel.sheet_panel_list.append([sheet, self.location])
				out_list.append([sheet, self.location])
		return out_list


reload = IN[1]  # type: ignore

# get all panel instances
panels_list = FilteredElementCollector(doc).\
	OfCategory(BuiltInCategory.OST_ElectricalEquipment).\
	WhereElementIsNotElementType().\
	ToElements()

# get all sheets
sheets_list = FilteredElementCollector(doc).\
	OfCategory(BuiltInCategory.OST_Sheets).\
	WhereElementIsNotElementType().\
	ToElements()

map(lambda x: Panel(x).add_info_to_list(), panels_list)

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

for sheet in Panel.sheet_panel_list:
	sheet_inst = sheet[0]
	sheet_location = sheet[1]
	sheet_inst.LookupParameter("Shop Name").Set(sheet_location)

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = Panel.sheet_panel_list
