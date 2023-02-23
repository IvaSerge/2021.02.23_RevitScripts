import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

dir_path = IN[0].DirectoryName  # type: ignore
sys.path.append(dir_path)

import System
from System import Array
from System.Collections.Generic import *

System.Threading.Thread.CurrentThread.CurrentCulture = System.Globalization.CultureInfo("en-US")
from System.Runtime.InteropServices import Marshal

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
import toolsrvt
# from toolsrvt import test

# get panel

# get circuits of the panel

# get circuit parameters to transfer to 2D diagramm

# get shedule

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

OUT = toolsrvt.test()
