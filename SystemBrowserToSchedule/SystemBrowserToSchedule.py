import clr
import sys

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

# ================ local imports
import toolsrvt
from toolsrvt import *

import rvt_panel
reload(rvt_panel)
from rvt_panel import *

import tree_list_utils
reload(tree_list_utils)

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
	sel_elem = UnwrapElement(rvt_elem)  # type: ignore
else:
	sel_elem = uidoc.Selection.PickObject(
		Autodesk.Revit.UI.Selection.ObjectType.Element,
		"Element selection")

main_panel:RvtPanel = RvtPanel(sel_elem)
main_panel_name = sel_elem.Name
main_panel_tree = main_panel.get_circuts_info() 

circuits_tree = [[None, main_panel_name]] + main_panel_tree
flattened_result = tree_list_utils.flatten_with_none(circuits_tree)
print(flattened_result)

excel_name_panel = tree_list_utils.create_file_name(main_panel_name, dir_path)
excel_name_template = tree_list_utils.create_file_name("temp", dir_path)
tree_list_utils.create_new_xlsx(excel_name_template, excel_name_panel)
tree_list_utils.write_totals(excel_name_panel, flattened_result)


OUT = flattened_result
