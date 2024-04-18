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
from abc import ABC, abstractmethod
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
	@abstractmethod
	def _get_rev_objects(cls):
		...

	@classmethod
	@abstractmethod
	def _get_objects_parameters(self):
		...

	@classmethod
	@abstractmethod
	def _get_objects_parameters(self):
		...

	@classmethod
	@abstractmethod
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
		elem_change_num = [
			toolsrvt.get_parval(i, "BOQ Phase")
			for i in elems_list]

		return list(zip(elem_categories, elem_description, elem_reference, elem_change_num))

	def get_boq(self, bic_string):
		rvt_elems = self._get_rev_objects(bic_string)
		if not rvt_elems:
			return None
		rvt_params_list = self._get_objects_parameters(rvt_elems)
		category_name = rvt_elems[0].Category.Name 

		groupped_list = self.get_groupped_list(rvt_params_list)

		# first two rows are hard-coded for the method
		# empty stirngs needed for correct zip and insert in Excel
		row_1 = [category_name, " ", " ", " ", " "]
		row_2 = ["Description", "Count", "Product reference", "Change number", "Comments"]
		out_list = []
		out_list.append(row_1)
		out_list.append(row_2)
		out_list.extend(groupped_list)

		return out_list

	@staticmethod
	def get_groupped_list(_not_sorted_list):

		pd_col_1 = pd.Series([i[0] for i in _not_sorted_list])
		pd_col_2 = pd.Series([i[1] for i in _not_sorted_list])
		pd_col_3 = pd.Series([i[2] for i in _not_sorted_list])
		pd_col_4 = pd.Series([i[3] for i in _not_sorted_list])

		pd_elems_frame = pd.DataFrame({
			"Column_1": pd_col_1,
			"Column_2": pd_col_2,
			"Column_3": pd_col_3,
			"Column_4": pd_col_4
			})

		df_groupped_by = pd_elems_frame.groupby(["Column_1", "Column_2", "Column_3","Column_4"])["Column_2"].indices.keys()
		out_column_2 = [i[1] for i in df_groupped_by]
		out_column_3 = [i[2] for i in df_groupped_by]
		out_count = pd_elems_frame.groupby(["Column_1", "Column_2"]).size().tolist()
		out_column_4 = [i[3] for i in df_groupped_by]

		out_list = list(zip(out_column_2, out_count, out_column_3, out_column_4))
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
		row_1 = ["Cable", " ", " ", " ", " "]
		row_2 = ["Description", "Length", "Length +20% spare, m", "Change number", "Comments"]
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

		doc = rvt_elems[0].Document
		# filter trays, that not have type mark
		rvt_elems = [i for i in rvt_elems if
			toolsrvt.get_parval(
				doc.GetElement(i.GetTypeId()), 
				"WINDOW_TYPE_ID")]

		out_list = []
		row_1 = ["Cable trays", " ", " ", " ", " "]
		row_2 = ["Description", "Lngth,m", "Product reference", "Change number", "Comments"]
		out_list.append(row_1)
		out_list.append(row_2)
		out_list.extend(boq_analyze.get_boq_by_l_based_fam(rvt_elems))

		return out_list

class tsla_fittings(electrical_objects):

	def __init__(self):
		self.sort_str = "Cable trays fittings"
		self.boq = self.get_boq()

	def get_boq(self):
		rvt_elems = self._get_rev_objects("OST_CableTrayFitting")
		if not rvt_elems:
			return None

		elems_boq = boq_analyze.get_boq_by_tray_fitting(rvt_elems)
		elems_groupped = self.get_groupped_list(elems_boq)

		out_list = []
		row_1 = [self.sort_str, " ", " ", " ", " "]
		row_2 = ["Description", "Count", "Product reference", "Change number", "Comments"]
		out_list.append(row_1)
		out_list.append(row_2)
		out_list.extend(elems_groupped)

		# return out_list
		return out_list

class conduit_as_grounding(electrical_objects):

	def __init__(self):
		self.sort_str = "Grounding"
		self.boq = self.get_boq()

	def get_boq(self):
		rvt_elems = self._get_rev_objects("OST_Conduit")	
		if not rvt_elems:
			return None

		# additional filtering of the elements to get grounding only
		rvt_elems = [i for i in rvt_elems if 
			toolsrvt.get_parval(
			i.Document.GetElement(i.GetTypeId()),
			"ALL_MODEL_TYPE_COMMENTS") == "Electrical grounding"]

		out_list = []
		row_1 = ["Grounding system", " ", " ", " ", " "]
		row_2 = ["Description", "Lngth,m", "Product reference", "Change number", "Comments"]
		out_list.append(row_1)
		out_list.append(row_2)
		out_list.extend(boq_analyze.get_boq_by_l_based_fam(rvt_elems))

		return out_list

class data_objects(electrical_objects):

	def __init__(self):
		additional_devices = None
		self.sort_str = "Data devices"
		self.boq = self.get_boq("OST_DataDevices")

		if self.boq:
			additional_devices = self.get_additional_elems()
		if additional_devices:
			self.boq.extend(additional_devices)

	def get_additional_elems(self):
		elems_list = self.boq
		additional_elems = []
		change_num = self.boq_param_value

		for elem in elems_list:
			if "socket" in elem[0].lower():
				to_add = ["Data devices", "Jack Category 6A scielded", "Tesla product standard B.4.1", change_num]
				couter = int(elem[1])
				additional_elems.extend([to_add] * couter)
			elif "access point" in elem[0].lower():
				to_add = ["Data devices", "Patch cable category 6A schielded", "Not product specific", change_num]
				couter = int(elem[1])
				additional_elems.extend([to_add] * couter)

			elif "hard wired" in elem[0].lower():
				to_add = ["Data devices", "Jack Category 6A scielded", "Tesla product standard B.4.1", change_num]
				couter = int(elem[1])
				additional_elems.extend([to_add] * couter * 2)
			else:
				pass

		groupped_list = self.get_groupped_list(additional_elems)
		return groupped_list
