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

global doc
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView

# ================ Python imports
import importlib
from importlib import reload
import toolsrvt
reload(toolsrvt)
from toolsrvt import *
toolsrvt.UnwrapElement = UnwrapElement  # type: ignore
import itertools


reload = IN[1]  # type: ignore

# get panel
panel_inst = toolsrvt.unwrap(IN[3])  # type: ignore
circuits = elsys_by_brd(panel_inst)[1]

# get circuit parameters to transfer to 2D diagramm
circuits_param_to_set = ["RBS_ELEC_CIRCUIT_FRAME_PARAM"]
circuit = circuits[0]
circuits_par_val = [[circuit, get_parval(circuit, i)] for i in circuits_param_to_set]


# isPanel
# referTo (layout)


# get shedule
shedule_name = IN[2]  # type: ignore

# get 2D diagramms

# get shedule insert point

# calculate 2D families insert points

# insert shedule on the layout

# insert 2D diagramms on layout

# set parameters to 2D families


# # =========Start transaction
# TransactionManager.Instance.EnsureInTransaction(doc)

# # =========End transaction
# TransactionManager.Instance.TransactionTaskDone()

# OUT = dir(UnwrapElement)
OUT = circuits_par_val
