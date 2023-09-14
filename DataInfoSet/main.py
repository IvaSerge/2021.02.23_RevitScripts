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
shortest_grid_name = grid.get_nearest_grid_by_instance(rvt_elem)
params_to_set.append([rvt_elem, "TO Grid", shortest_grid_name])
elem_level = get_level_name(rvt_elem)
# floor

# find ciruit
# for circuit find panel info

# combine circuit and elem parameters to multi-text parameter


OUT = elem_level
