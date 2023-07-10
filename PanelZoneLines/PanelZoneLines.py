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
import System
from System import Array
from System.Collections.Generic import *

import importlib
from importlib import reload

# ================ local imports
import toolsrvt
reload(toolsrvt)
from toolsrvt import *

# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView

reload_IN = IN[1]  # type: ignore
rvt_panel = UnwrapElement(IN[2])  # type: ignore
line_style_str = IN[3]  # type: ignore

if view.ViewType != Autodesk.Revit.DB.ViewType.FloorPlan:
	raise ValueError("Current View is not a Floor Plan")

xyz_panel = rvt_panel.Location.Point
xyz_panel = XYZ(xyz_panel.X, xyz_panel.Y, 0)

# get circuits
panel_low_circuits = toolsrvt.elsys_by_brd(rvt_panel)[1]

# for every circuit get elements
elem_list = list()
for circuit in panel_low_circuits:
	elem_list.extend(circuit.Elements)

# for every element create line
lines_list = list()
for elem in elem_list:
	xyz_elem = elem.Location.Point
	xyz_elem = XYZ(xyz_elem.X, xyz_elem.Y, 0)
	panel_elem_line = Autodesk.Revit.DB.Line.CreateBound(xyz_panel, xyz_elem)
	lines_list.append(panel_elem_line)

# get linestile by name
line_styles = FilteredElementCollector(doc).OfClass(GraphicsStyle).ToElements()
line_style = [x for x in line_styles if x.Name == line_style_str][0]

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# create detail lines
for ln in lines_list:
	rvt_ln = doc.Create.NewDetailCurve(view, ln)
	rvt_ln.LineStyle = line_style


# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = line_style
