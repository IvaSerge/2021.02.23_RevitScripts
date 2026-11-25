
"""modue to represent architectural grid"""
import clr

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

# ================ Python imports
import math
from operator import itemgetter
import json
import os

import toolsrvt


def _load_level_names():
	json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db_level_names.json")
	with open(json_path, "r", encoding="utf-8") as f_db:
		return json.load(f_db)


def get_level_name(rvt_elem: Autodesk.Revit.DB.FamilyInstance) -> str:
	"""
	Get Level from the element.\\
	Return string that represents level name according to Naming Standard.
	Model and level names are taken from db_level_names.json.
	"""
	doc = rvt_elem.Document
	doc_title = doc.Title
	level_db = _load_level_names()

	# JSON top-level key must be contained in the document title
	matched_key = None
	for model_key in level_db:
		if model_key in doc_title:
			if matched_key is None or len(model_key) > len(matched_key):
				matched_key = model_key

	if not matched_key:
		print(doc_title)
		raise ValueError("No information about model levels in JSON")

	rvt_lvl = doc.GetElement(rvt_elem.LevelId)
	if not rvt_lvl or rvt_lvl.Id == -1:
		sh_lvl = toolsrvt.get_parval(rvt_elem, "INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM")
		rvt_lvl = doc.GetElement(sh_lvl)

	if not rvt_lvl:
		# raise ValueError("No Host Level found")
		return None

	rvt_level_str = rvt_lvl.Name
	level_map = {pair[0]: pair[1] for pair in level_db[matched_key]}
	if rvt_level_str not in level_map:
		print(rvt_level_str)
		raise ValueError("No information about level name found in JSON")

	return level_map[rvt_level_str]


def get_circuit_params(rvt_elem: Autodesk.Revit.DB.FamilyInstance, lvl_str, grid_str) -> str:
	
	outlist = []
	rvt_elem_cat = rvt_elem.Category.Id
		
	# Check if instance is electrical panel
	if rvt_elem_cat.IntegerValue == -2001040:
		el_systems = toolsrvt.elsys_by_brd(rvt_elem)[0]
	else:
		el_systems = rvt_elem.MEPModel.GetElectricalSystems()
	
	if not 	el_systems:
		return None
	
	if lvl_str:
		circuit_combained_location = f"{lvl_str} {grid_str}"
	else:
		circuit_combained_location = grid_str

	for el_system in el_systems:
		outlist.append([el_system, "Location", circuit_combained_location])

	return outlist

