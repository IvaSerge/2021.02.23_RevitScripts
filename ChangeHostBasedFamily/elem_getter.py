
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

import System
from System import Array
from System.Collections.Generic import *


# ================ Python imports
import json
import toolsrvt

def get_new_type(old_family_instance, json_file):
	# type: (FamilyInstance, str) -> FamilyType

	doc = old_family_instance.Document
	new_type = None
	old_type = doc.GetElement(old_family_instance.GetTypeId())
	old_type_name = old_type.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
	old_family_name = old_family_instance.Symbol.FamilyName
	json_data = get_json_data(old_family_name, old_type_name, json_file)
	new_fam_name = json_data[0]
	new_type = json_data[1]

	rvt_type = get_type_by_fam_and_type(doc, new_fam_name, new_type)
	if not rvt_type:
		error_text = f"Type not found in Revit: {new_fam_name}, {new_type}"
		print(error_text)
		raise ValueError(error_text)

	return rvt_type

def get_json_data(family_name, family_type, json_file):

	# read JSON
	with open(json_file, "r", encoding='utf-8') as f_db:
			data = json.load(f_db)

	try:
		j_data = data[family_name][family_type]
	except:
		error_text = f"Not found in database: {family_name}, {family_type}"
		print(error_text)
		raise ValueError(error_text)

	return j_data

def get_type_by_fam_and_type(doc, family_name, family_type):

	fnrvStr = FilterStringEquals()
	pvpType = ParameterValueProvider(ElementId(int(BuiltInParameter.SYMBOL_NAME_PARAM)))
	pvpFam = ParameterValueProvider(ElementId(int(BuiltInParameter.ALL_MODEL_FAMILY_NAME)))

	fruleF = FilterStringRule(pvpFam, fnrvStr, family_name)
	filterF = ElementParameterFilter(fruleF)

	fruleT = FilterStringRule(pvpType, fnrvStr, family_type)
	filterT = ElementParameterFilter(fruleT)

	filter = LogicalAndFilter(filterT, filterF)

	elem_new_rvt_type = FilteredElementCollector(doc).\
		WhereElementIsElementType().\
		WherePasses(filter).\
		FirstElement()

	return elem_new_rvt_type
