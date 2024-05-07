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

clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *


# Import Element wrapper extension methods
clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
clr.ImportExtensions(Revit.GeometryConversion)

# ================ Python imports
import System
from importlib import reload
from operator import itemgetter

# ================ local imports
import toolsrvt
reload(toolsrvt)

# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView

reload_IN = IN[1]  # type: ignore

# there is category
bic = System.Enum.Parse(BuiltInCategory, IN[2])  # type: ignore
rvt_instances = FilteredElementCollector(doc).\
	OfCategory(bic).\
	WhereElementIsNotElementType().\
	ToElements()

# # =========Start transaction
# TransactionManager.Instance.EnsureInTransaction(doc)

# # =========End transaction
# TransactionManager.Instance.TransactionTaskDone()

OUT = rvt_instances
