import clr
import os
import sys

# ================ Revit imports
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# ================ Python imports
from importlib import reload
from abc import ABC, abstractclassmethod
from System import Array
from System.Collections.Generic import *
import pandas as pd

# ================ local imports
import toolsrvt
reload(toolsrvt)


class RvtObjGroup(ABC):
	"""
	Class represents groups of Revit objects, groupped by common properties.
	As example: groupped by category
	"""
	
	@classmethod
	@abstractclassmethod
	def get_rev_objects(cls):
		...

	@abstractclassmethod
	def get_objects_parameters(self):
		...

	@abstractclassmethod
	def get_objects_description(self):
		...

	@abstractclassmethod
	def get_boq(self):
		...

class electrical_objects(RvtObjGroup):
	"""
		Class creates and works with sorted by Category elements.
	"""

	doc: Document = None
	boq_parameter: str = None
	boq_param_value: str = None

	def _init_(self, bic_string):
		self.boq = self.get_boq(bic_string)
		self.sort_str = bic_string

	def get_rev_objects(cls, bic_string):
		"""
			get all elements by BuiltInCategory string
			and BOQ name
		"""

		# =============  parameter filter
		parameter_id = [
			i for i in
			FilteredElementCollector(cls.doc).OfClass(ParameterElement)
			if i.Name == cls.boq_parameter]
		if parameter_id:
			parameter_id = parameter_id[0].Id
		else:
			error_str = "Parameter not found"
			raise ValueError(error_str)

		parameter_value_provider = ParameterValueProvider(parameter_id)
		parameter_str_rule = FilterStringRule(
			parameter_value_provider,
			FilterStringEquals(),
			cls.boq_param_value)

		parameter_filter = ElementParameterFilter(parameter_str_rule)

		# =============  category filter
		bic_id = toolsrvt.category_by_bic_name(cls.doc, bic_string).Id

		bic_filter = ElementCategoryFilter(bic_id)

		main_filter = LogicalAndFilter(bic_filter, parameter_filter)
		elems = FilteredElementCollector(cls.doc).WherePasses(main_filter).ToElements()
		return elems

	def get_objects_parameters(self, elems_list):
		elem_categories = [i.Category.Name for i in elems_list]
		elem_description = [
			toolsrvt.get_parval(i.Symbol, "ALL_MODEL_DESCRIPTION")
			for i in elems_list]
		elem_reference = [
			toolsrvt.get_parval(i.Symbol, "ALL_MODEL_MANUFACTURER")
			for i in elems_list]

		return zip(elem_categories, elem_description)

	def get_boq(self, bic_string):
		rvt_elems = self.get_rev_objects(bic_string)
		rvt_params_list = self.get_objects_parameters(rvt_elems)

		pd_row_1 = pd.Series(rvt_params_list[0])
		pd_row_2 = pd.Series(rvt_params_list[1])
		pd_row_3 = pd.Series(rvt_params_list[2])

		pd_elems_frame = pd.DataFrame({
			"Category": pd_row_1,
			"Description": pd_row_2,
			"Manufacturer": pd_row_3})

		df_groupped_by = pd_elems_frame.groupby(["Category", "Description", "Manufacturer"])["Description"].indices.keys()
		out_description = [i[1] for i in df_groupped_by]
		out_manufacturer = [i[2] for i in df_groupped_by]
		out_count = pd_elems_frame.groupby(["Category", "Description"]).size().tolist()

		# first two rows are hard-coded for the method
		# empty stirngs needed for correct zip and insert in Excel
		row_1 = [bic_string, " ", " "]
		row_2 = ["Description", "Count", "Product reference", "Comments"]

		out_list = []
		out_list.append(row_1)
		out_list.append(row_2)
		out_list.extend(
			list(zip(out_description, out_manufacturer, out_count)))
		


