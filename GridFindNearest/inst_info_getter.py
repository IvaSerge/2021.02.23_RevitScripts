
"""modue to represent architectural grid"""
import clr

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

# ================ Python imports
import math
from operator import itemgetter
import re

import toolsrvt


def get_level_name(rvt_elem: Autodesk.Revit.DB.FamilyInstance) -> str:
	"""
	Get Level from the element.\\
	Return string that represents level name according to Naming Standard
	"""
	doc = rvt_elem.Document
	doc_titel = doc.Title
	rvt_lvl = doc.GetElement(rvt_elem.LevelId)
	if not rvt_lvl:
		sh_lvl = toolsrvt.get_parval(rvt_elem, "INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM")
		rvt_lvl = doc.GetElement(sh_lvl)

	if not rvt_lvl:
		# raise ValueError("No Host Level found")
		return None
	rvt_level_str = rvt_lvl.Name
	
	# level naming is model specific
	# F level (1F, 2F..)
	is_f_level = any([
		"BER-GF-SE-CP" in doc_titel, 
		"BER-GF-SITE-PTP" in doc_titel, 
		])

	if is_f_level:
		# for CP only
		regexp = re.compile(r"^(.*?)[FM]")
		check = regexp.match(rvt_level_str)
		rvt_level_out = check.group(1)

	elif "BER-GF-SITE-NPI" in doc_titel:
		if "RF" in rvt_level_str:
			rvt_level_out = "3F"	# for NPI only - 1M and 2F are the same
		elif "1M" in rvt_level_str:
			rvt_level_out = "2F"
		elif "1F" in rvt_level_str:
			rvt_level_out = "1F"
		else:
			raise ValueError("Wrong level name")

	elif "BER-GF-SE-DU" in doc_titel:
		# for DU only - 1M and 2F are the same
		if "2F" in rvt_level_str or "1M" in rvt_level_str:
			rvt_level_out = "2"
		elif "1F" in rvt_level_str:
			rvt_level_out = "1"
		else:
			raise ValueError("Wrong level name")
	elif rvt_level_str:
		return rvt_level_str
	else:
		raise ValueError("Model not found. Add level settings for the model")

	return rvt_level_out


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


