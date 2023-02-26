"""
This module to represent 2D diagramm
"""


import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import System
from System import Array
from System.Collections.Generic import *

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

# ================ Dynamo imports
clr.AddReference('ProtoGeometry')
import Autodesk.DesignScript

from Autodesk.DesignScript.Geometry import *

clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
from Revit.Elements import *
clr.ImportExtensions(Revit.GeometryConversion)
clr.ImportExtensions(Revit.GeometryReferences)

# ================ Python imports
import importlib
from importlib import reload

# ================ local imports
import toolsrvt
reload(toolsrvt)


class Diagramm():
	def __init__(self):
		self.isert_point = None
		self.params = list()
		self.symbol_type = None
		self.instance = None

	def create_diag_on_sheet(self, doc, _sheet):
		dia_inst = doc.Create.NewFamilyInstance(
			self.isert_point,
			self.symbol_type,
			_sheet)
		return dia_inst

	def set_parameters(self):
		for param_info in self.params:
			param_name = param_info[0]
			param_val = param_info[1]
			toolsrvt.setup_param_value(
				self.instance,
				param_name,
				param_val)

		return param_name, param_val

	@staticmethod
	def get_shedule_view(doc, panel_inst, view_inst):
		panel_name = panel_inst.Name
		shedule_view = None
		shedule_graphics = None

		# check if shedule view is on sheet
		# If found - No action requiered
		owner_filter = ElementOwnerViewFilter(view_inst.Id)
		shedule_graphics = FilteredElementCollector(doc).\
			OfCategory(BuiltInCategory.OST_PanelScheduleGraphics).\
			WhereElementIsNotElementType().\
			WherePasses(owner_filter).\
			ToElements()
		shedule_graphics = [i for i in shedule_graphics if panel_name in i.Name]
		if shedule_graphics:
			return None

		# get shedule view
		shedule_view = FilteredElementCollector(doc).\
			OfClass(Autodesk.Revit.DB.Electrical.PanelScheduleView).\
			WhereElementIsNotElementType().\
			ToElements()
		shedule_view = [i for i in shedule_view if i.Name == panel_name]
		if shedule_view:
			shedule_view = shedule_view[0]
		return shedule_view

	def get_circuit_symbol(self, circuit: Autodesk.Revit.DB.Electrical.ElectricalSystem):
		# NONE (Spare or Space)
		if circuit.CircuitType != Autodesk.Revit.DB.Electrical.CircuitType.Circuit:
			return None

		# Check if element in the circuit is panel.
		# 1. Circuit contains only 1 element
		# 2. This element is electrical panel by category
		# 3. Element not Quasy
		circuit_first_element = list(circuit.Elements)[0]
		elem_is_alone = len(list(circuit.Elements)) == 1  # 1
		elem_category = circuit_first_element.Category.Id == ElementId(-2001040)
		elem_not_quasy = "QUASI" not in circuit_first_element.Symbol.Family.Name
		elem_is_panel = all([elem_is_alone, elem_category, elem_not_quasy])
		if elem_is_panel:
			self.params.append(["Panel", 1])

		# get reference
		if elem_is_panel:
			refer_sheet = toolsrvt.inst_by_cat_strparamvalue(
				BuiltInCategory.OST_Sheets,
				BuiltInParameter.SHEET_NAME,
				circuit.LoadName,
				False)
			if refer_sheet:
				refer_sheet = refer_sheet[0]
				refer_sheet_number = refer_sheet.SheetNumber
				self.params.append(["Reference", refer_sheet_number])
				return None
			else:
				self.params.append(["Reference", "N/A"])
				return None

		# POC symbol - all other
		self.params.append(["POC", 1])
