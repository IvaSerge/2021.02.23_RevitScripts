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
import boq_analyze


class RvtObjGroup(ABC):
	"""
	Class represents groups of Revit objects, groupped by common properties.
	As example: groupped by category
	"""
	
	@classmethod
	@abstractclassmethod
	def _get_rev_objects(cls):
		...

	@abstractclassmethod
	def _get_objects_parameters(self):
		...

	@abstractclassmethod
	def _get_objects_parameters(self):
		...

	@abstractclassmethod
	def get_boq(self):
		...
	
	# class properties
	doc = None
	boq_parameter = None
	boq_param_value = None

class electrical_objects(RvtObjGroup):
	"""
		Class creates and works with sorted by Category elements.
	"""

	def __init__(self, bic_string):
		self.boq = self.get_boq(bic_string)
		self.sort_str = toolsrvt.category_by_bic_name(
			self.doc, bic_string).Name
	
	def __lt__(self, other):
		return self.sort_str < other.sort_str

	def __repr__(self) -> str:
		return self.sort_str

	def _get_rev_objects(cls, bic_string):
		"""
			get all elements by BuiltInCategory string
			and BOQ name
		"""

		elems = toolsrvt.inst_by_multicategory_param_val(
			cls.doc,
			[bic_string],
			cls.boq_parameter,
			cls.boq_param_value)

		return elems

	def _get_objects_parameters(self, elems_list):
		elem_categories = [i.Category.Name for i in elems_list]
		elem_description = [
			toolsrvt.get_parval(i.Symbol, "ALL_MODEL_DESCRIPTION")
			for i in elems_list]
		elem_reference = [
			toolsrvt.get_parval(i.Symbol, "ALL_MODEL_MANUFACTURER")
			if toolsrvt.get_parval(i.Symbol, "ALL_MODEL_MANUFACTURER")
			else " "
			for i in elems_list]

		return list(zip(elem_categories, elem_description, elem_reference))

	def get_boq(self, bic_string):
		rvt_elems = self._get_rev_objects(bic_string)
		if not rvt_elems:
			return None
		rvt_params_list = self._get_objects_parameters(rvt_elems)
		category_name = rvt_elems[0].Category.Name 

		pd_row_1 = pd.Series([i[0] for i in rvt_params_list])
		pd_row_2 = pd.Series([i[1] for i in rvt_params_list])
		pd_row_3 = pd.Series([i[2] for i in rvt_params_list])

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
		row_1 = [category_name, " ", " ", " "]
		row_2 = ["Description", "Count", "Product reference", "Comments"]
		out_list = []
		out_list.append(row_1)
		out_list.append(row_2)
		out_list.extend(
			list(zip(out_description, out_count, out_manufacturer)))

		return out_list

class electrical_circuits(electrical_objects):

	def __init__(self):
		self.sort_str = "Cables"
		self.boq = self.get_boq()

	def get_boq(self):
		rvt_elems = self._get_rev_objects("OST_ElectricalCircuit")
		if not rvt_elems:
			return None

		out_list = []
		row_1 = ["Cable", " ", " ", " "]
		row_2 = ["Description", "Length", "Length +20% spare, m", "Comments"]
		out_list.append(row_1)
		out_list.append(row_2)
		out_list.extend(boq_analyze.get_boq_by_circuits(rvt_elems))

		return out_list

class tsla_trays(electrical_objects):

	def __init__(self):
		self.sort_str = "Cable trays"
		self.boq = self.get_boq()

	def get_boq(self):
		rvt_elems = self._get_rev_objects("OST_CableTray")
		if not rvt_elems:
			return None

		out_list = []
		row_1 = ["Cable trays", " ", " ", " "]
		row_2 = ["Description", "Length,m", "Product reference", "Comments"]
		out_list.append(row_1)
		out_list.append(row_2)
		out_list.extend(boq_analyze.get_boq_by_l_based_fam(rvt_elems))

		return out_list
