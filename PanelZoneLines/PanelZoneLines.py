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

# check current view. It need to be plan view.
if view.ViewType != Autodesk.Revit.DB.ViewType.FloorPlan:
	raise ValueError("Current View is not a Floor Plan")


# get panel and it location point
# get circuits
# for every circuit get elements

# for every element create line
# Line.CreateBound(panel_XYZ, element_XYZ);


# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# get linestile by name
# for every line create detail line


# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = view.ViewType == Autodesk.Revit.DB.ViewType.FloorPlan
