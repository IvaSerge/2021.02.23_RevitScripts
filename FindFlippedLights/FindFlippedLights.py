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

lightings = FilteredElementCollector(doc).\
	OfCategory(BuiltInCategory.OST_LightingFixtures).\
	WhereElementIsNotElementType().\
	ToElements()

outlist = list()
for lighting in lightings:
	try:
		chec_if_flipped = lighting.IsWorkPlaneFlipped
	except:
		chec_if_flipped = False

	# electrical system not found
	if chec_if_flipped:
		outlist.append(lighting.Id.ToString())


OUT = outlist
