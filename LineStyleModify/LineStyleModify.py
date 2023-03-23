# ================ system imports
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
sys.path.append(IN[0].DirectoryName)  # type: ignore

import System
from System import Array
from System.Collections.Generic import *

# ================ Revit imports
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager


doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application

reload = IN[1]  # type: ignore
g_name = IN[2]  # type: ignore

g_styles = FilteredElementCollector(doc).\
	OfClass(Autodesk.Revit.DB.GraphicsStyle)

g_style = [i for i in g_styles if i.Name == g_name][0]

# Change color
g_color = Autodesk.Revit.DB.Color(0, 0, 255)  # blue


# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

g_style.GraphicsStyleCategory.LineColor = g_color

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = g_style.GraphicsStyleCategory.LineColor.Red, g_style.GraphicsStyleCategory.LineColor.Green, g_style.GraphicsStyleCategory.LineColor.Blue
