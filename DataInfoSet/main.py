import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

dir_path = IN[0].DirectoryName  # type: ignore
sys.path.append(dir_path)


# ================ Revit imports
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# ================ Python imports
from System import Array
from System.Collections.Generic import *
from importlib import reload
import re

# ================ local imports
import toolsrvt
reload(toolsrvt)
from toolsrvt import *
import grid
reload(grid)
from grid import *


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
		raise ValueError("No Host Level found")
	rvt_level_str = rvt_lvl.Name
	
	# level naming is model specific
	if "BER-GF-SE-CP" in doc_titel:
		# for CP only
		regexp = re.compile(r"^(.*?)F")
		check = regexp.match(rvt_level_str)
		rvt_level_out = check.group(1)

	elif "BER-GF-SE-DU" in doc_titel:
		# for DU only - 1M and 2F are the same
		if "2F" in rvt_level_str or "1M" in rvt_level_str:
			rvt_level_out = "2"
		elif "1F" in rvt_level_str:
			rvt_level_out = "1"
		else:
			raise ValueError("Wrong level name")
	else:
		raise ValueError("Model not found. Add level settings for the model")

	return rvt_level_out

def get_elements_by_panel(rvt_panel):
	panel_circuits = rvt_panel.MEPModel.GetAssignedElectricalSystems()
	panel_circuits = [i for i in panel_circuits
		if i.SystemType == Electrical.ElectricalSystemType.Data]

	if not panel_circuits:
		return None

	elem_list = list()
	for data_circuit in panel_circuits:
		circuit_elements = list(data_circuit.Elements)
		elem_list.extend(circuit_elements)

	# clean list by Id
	id_list = list()
	elem_list_filtered = list()
	for elem in elem_list:
		elem_Id = elem.Id.IntegerValue
		if elem_Id not in id_list:
			id_list.append(elem_Id)
			elem_list_filtered.append(elem)

	return elem_list_filtered


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView
reload_var = IN[1]  # type: ignore
rvt_elem = IN[2]  # type: ignore


# Element selection
if rvt_elem:
	rvt_elem = UnwrapElement(rvt_elem)  # type: ignore
else:
	sel_elem = uidoc.Selection.PickObject(
		Autodesk.Revit.UI.Selection.ObjectType.Element,
		"Selection of two elements")
	rvt_elem = doc.GetElement(sel_elem.ElementId)

if rvt_elem.Category.Id.IntegerValue != -2001040:
	elem_list = [rvt_elem]
else:
	elem_list = list()
	#  elem_list.append(rvt_elem)  # adding panel to the list is dangerous
	# TODO add bool that allow/not allow set panel parameters
	panel_elements = get_elements_by_panel(rvt_elem)
	elem_list.extend(panel_elements)

grid.find_grid_intersection_points(doc)

for rvt_elem in elem_list:
	# find element parameters
	params_to_set = list()
	elem_grid = grid.get_nearest_grid_by_instance(rvt_elem)

	# For TV clean grid name - Project specific change
	if elem_grid.startswith("TV-"):
		elem_grid = re.sub("-", "", elem_grid)
	elem_level = get_level_name(rvt_elem)
	elem_comments = toolsrvt.get_parval(rvt_elem, "ALL_MODEL_INSTANCE_COMMENTS")

	params_to_set.append([rvt_elem, "TO Grid", elem_grid])
	params_to_set.append([rvt_elem, "TO Level", elem_level])

	# find ciruit
	elem_circuits = rvt_elem.MEPModel.GetElectricalSystems()
	elem_circuits = [i for i in elem_circuits
		if i.SystemType == Electrical.ElectricalSystemType.Data]
	elem_circuits.sort(key=lambda x: x.StartSlot)

	# for each circuit fill in TO parameters
	multi_tag_list = list()
	for circuit in elem_circuits:
		# circuit_nuber = "{:02d}".format(int(circuit.Name))  # if heading zeros needed
		circuit_nuber = circuit.Name  # without heading zeros
		# drop info to circuit
		params_to_set.append([circuit, "TO Grid", elem_grid])
		params_to_set.append([circuit, "TO Level", elem_level])
		params_to_set.append([circuit, "ALL_MODEL_INSTANCE_COMMENTS", elem_comments])
		params_to_set.append([circuit, "RBS_ELEC_CIRCUIT_NAME", elem_comments])

		# panel info to circuit
		data_panel = circuit.BaseEquipment
		panel_grid = toolsrvt.get_parval(data_panel, "TO Grid")
		panel_level = toolsrvt.get_parval(data_panel, "TO Level")
		panel_patch_panel = toolsrvt.get_parval(data_panel, "TO Panel")
		panel_rack = toolsrvt.get_parval(data_panel, "TO Rack")

		# parameters to set from panel to circuit
		params_to_set.append([circuit, "TO Rack Grid", panel_grid])
		params_to_set.append([circuit, "TO Rack Floor", panel_level])
		params_to_set.append([circuit, "TO Panel", panel_patch_panel])
		params_to_set.append([circuit, "TO Rack", panel_rack])

		# multi_tag parameter for elemet
		try:
			circuit_tag = panel_level + panel_grid + "." + panel_rack
		except:
			error_text = "Panel parameters empty. Checl Level, Grid, Rack"
			raise ValueError(error_text)
		circuit_tag += "-" + elem_level + elem_grid + "."
		circuit_tag += panel_patch_panel + circuit_nuber
		multi_tag_list.append(circuit_tag)

	# convert multi_tag to string and set to element
	multi_tag_str = "\n".join(multi_tag_list)
	params_to_set.append([rvt_elem, "Multi_Tag_1", multi_tag_str])
	# circuit parameters to element
	params_to_set.append([rvt_elem, "TO Rack Grid", panel_grid])
	params_to_set.append([rvt_elem, "TO Rack Floor", panel_level])
	params_to_set.append([rvt_elem, "TO Panel", panel_patch_panel])
	params_to_set.append([rvt_elem, "TO Rack", panel_rack])

	# =========Start transaction
	TransactionManager.Instance.EnsureInTransaction(doc)
	for param_info in params_to_set:
		p_elem = param_info[0]
		p_name = param_info[1]
		p_value = param_info[2]
		toolsrvt.setup_param_value(p_elem, p_name, p_value)

	# =========End transaction
	TransactionManager.Instance.TransactionTaskDone()

if params_to_set:
	OUT = params_to_set
else:
	OUT = None
