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
	rvt_lvl = doc.GetElement(rvt_elem.LevelId)
	if not rvt_lvl:
		raise ValueError("No Host Level found")
	rvt_level_str = rvt_lvl.Name
	regexp = re.compile(r"^(.*?)_")
	check = regexp.match(rvt_level_str)
	rvt_level_str = check.group(1)
	return rvt_level_str

# def get_circtuit_parameters():


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

if rvt_elem.Category.Id != -2001040:
	elem_list = [rvt_elem]
else:
	# TODO: Info for panel and all elements in panel
	# check object category
	# if it is panel - find data circuit and first element of the data circuit
	# other - add to list
	pass

grid.find_grid_intersection_points(doc)

# find element parameters
params_to_set = list()
elem_grid = grid.get_nearest_grid_by_instance(rvt_elem)
elem_level = get_level_name(rvt_elem)

params_to_set.append([rvt_elem, "TO Grid", elem_grid])
params_to_set.append([rvt_elem, "TO Level", elem_level])


# find ciruit
elem_circuits = rvt_elem.MEPModel.GetElectricalSystems()
elem_circuits = [i for i in elem_circuits
	if i.SystemType == Electrical.ElectricalSystemType.Data]

# TODO sort circuits by Name

# for each circuit fill in TO parameters
multi_tag_list = list()
for circuit in elem_circuits:
	circuit_nuber = "{:02d}".format(int(circuit.Name))
	# drop info to circuit
	params_to_set.append([circuit, "TO Grid", elem_grid])
	params_to_set.append([circuit, "TO Level", elem_level])

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
	circuit_tag = panel_level + panel_grid + "." + panel_rack
	circuit_tag += "-" + elem_level + elem_grid + "."
	circuit_tag += panel_patch_panel + circuit_nuber
	multi_tag_list.append(circuit_tag)

# convert multi_tag to string and set to element
multi_tag_str = "\n".join(multi_tag_list)
params_to_set.append([rvt_elem, "Multi_Tag_1", multi_tag_str])

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)
for param_info in params_to_set:
	p_elem = param_info[0]
	p_name = param_info[1]
	p_value = param_info[2]
	toolsrvt.setup_param_value(p_elem, p_name, p_value)

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()


OUT = params_to_set
