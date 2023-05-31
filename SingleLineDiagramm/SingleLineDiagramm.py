import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

dir_path = IN[0].DirectoryName  # type: ignore
sys.path.append(dir_path)


# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# ================ Python imports
import collections
from collections import deque

import importlib
from importlib import reload

# ================ local imports
import toolsrvt
reload(toolsrvt)
from toolsrvt import *

import el_panel
reload(el_panel)


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView

reload_IN = IN[1]  # type: ignore
rvt_start_panel = UnwrapElement(IN[2])  # type: ignore

# select view for diagramm
sheet_element = UnwrapElement(IN[3])  # type: ignore
sheet_diagramm_id = sheet_element.OwnerViewId
sheet_diagramm = doc.GetElement(sheet_diagramm_id)

el_panel.el_panel.sheet = sheet_diagramm

panels_list = el_panel.panels_by_start_panel(rvt_start_panel)

for i, panel in enumerate(panels_list):
	panel.point_by_index()
	panel.get_anno_type()
	panel.get_distance_to_previous(panels_list, i)
	panel.get_panel_parameters()
	panel.get_control_circuit_parameters()
	# circiut parameters for CP model only. Not actual any more
	# panel.get_circuit_parameters()

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

for panel in panels_list:
	panel.create_elem_on_sheet()
	panel.set_parameters()


# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = [[i.rvt_panel, i.index_column, i.index_row, i.parameters_to_set] for i in panels_list]
