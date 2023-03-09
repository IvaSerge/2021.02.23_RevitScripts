"""
This module to represent shedules and legends
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
import re

# ================ local imports
import toolsrvt
reload(toolsrvt)
import diag
reload(diag)


class Shedule(diag.Diagramm):
	# hard coded parameters

	shedule_origin = XYZ(-1.15591572531952, 1.87274442257217, 0)
	elevation_origin = XYZ(0.476593699179163, 1.55815285531456, 0)
	elevation_type = None
	notes_origin = XYZ(0.480601866060708, 0.602081540683848, 0)
	notes_type = None

	def __init__(self, sheet_rvt):
		# type: (Shedule, ViewSheet) -> Shedule
		self.sheet = sheet_rvt
		self.insert_point = None
		self.params = list()
		self.symbol_type = None
		self.instance = None
		self.doc = sheet_rvt.Document

	@classmethod
	def set_diag_types(cls, doc):
		cls.notes_type = toolsrvt.inst_by_cat_strparamvalue(
			doc,
			BuiltInCategory.OST_Views,
			BuiltInParameter.VIEW_NAME,
			"E_Panel_General Notes",
			False)[0]

	def get_shedule_view(self, panel_inst):
		panel_name = panel_inst.Name
		view_inst = self.sheet
		doc = self.doc
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
			self.symbol_type = shedule_view
			self.insert_point = self.shedule_origin

	def get_elevation_symbol(self, panel):
		# get panel model
		panel_type_str = panel.Symbol.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()
		regexp = re.compile(r"TYPE\s\d\D\d?")
		type_name = regexp.search(panel_type_str).group(0)

		# get type by name
		shedule_view = toolsrvt.inst_by_cat_strparamvalue(
			self.doc,
			BuiltInCategory.OST_Views,
			BuiltInParameter.VIEW_NAME,
			type_name, False)
		self.symbol_type = shedule_view[0]

	def create_elem_on_sheet(self):
		if not self.symbol_type:
			return None
		doc = self.doc

		if isinstance(self.symbol_type, Autodesk.Revit.DB.Electrical.PanelScheduleView):
			self.instance = Electrical.PanelScheduleSheetInstance.Create(
				doc, self.symbol_type.Id, self.sheet)
			self.instance.Origin = self.insert_point
		else:
			if Autodesk.Revit.DB.Viewport.CanAddViewToSheet(doc, self.sheet.Id, self.symbol_type.Id):
				Autodesk.Revit.DB.Viewport.Create(
					doc,
					self.sheet.Id,
					self.symbol_type.Id,
					self.insert_point)
