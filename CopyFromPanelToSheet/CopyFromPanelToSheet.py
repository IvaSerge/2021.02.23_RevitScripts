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

	def find_related_sheet(self):
		global sheets_list
		return_list = list()
		for sheet in sheets_list:
			if self.panel_name in sheet.Name:
				return_list.append(sheet)
		return return_list


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

# for each panel create class instance
# find related lists
# add info to a global list
# for each panel find

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)


# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = Panel(panels_list[100]).on_sheets
