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

fnrvStr = FilterStringBeginsWith()
pvp = ParameterValueProvider(ElementId(int(BuiltInParameter.ELEM_FAMILY_PARAM)))
frule = FilterStringRule(pvp, fnrvStr, "E", True)
filter = ElementParameterFilter(frule)

lightings = FilteredElementCollector(doc).\
	OfCategory(BuiltInCategory.OST_LightingFixtures).\
	WhereElementIsNotElementType().\
	WherePasses(filter).\
	ToElements()

outlist = list()
for lighting in lightings:
	el_sys = lighting.MEPModel.GetElectricalSystems()

	# electrical system not found
	if not el_sys:
		outlist.append(lighting.Id.ToString())
		continue

	# light not connected to the panel
	el_sys = list(el_sys)
	panel_name = el_sys[0].PanelName
	if not panel_name:
		outlist.append(lighting.Id.ToString())
		continue

	# check panel name CP1-KE3W2C05 or CP1-KE3L2B05
	emerg_panel = any(
		[
			"CP1-KE3W2C05" in panel_name,
			"CP1-KE3L2B05" in panel_name
		])

	if not emerg_panel:
		outlist.append(lighting.Id.ToString())

OUT = outlist
