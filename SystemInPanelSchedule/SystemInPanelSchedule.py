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

# ================ Python imports


# ================ GLOBAL VARIABLES
uiapp = DocumentManager.Instance.CurrentUIApplication
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
app = uiapp.Application

global doc  # type: ignore
doc = DocumentManager.Instance.CurrentDBDocument


reload = IN[1]  # type: ignore[reportUndefinedVariable]
panel_name = IN[2]  # type: ignore

outlist = list()
error_list = list()

all_views = FilteredElementCollector(doc).\
	OfClass(Autodesk.Revit.DB.Electrical.PanelScheduleView).\
	WhereElementIsNotElementType()

view_in_work = [x for x in all_views
	if doc.GetElement(x.GetPanel()).Name == panel_name][0]


OUT = view_in_work.Name
