
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
# pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
# sys.path.append(pyt_path)
sys.path.append(IN[0].DirectoryName)  # type: ignore

import System
from System import Array
from System.Collections.Generic import *

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

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

reload = IN[1]  # type: ignore
search_str = IN[2]  # type: ignore

# For filtering find id of "Cable tray ID" parameter of electrical circuit
first_circuit = el_sys = FilteredElementCollector(doc).\
	OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_ElectricalCircuit).\
	WhereElementIsNotElementType().\
	FirstElement()
param_id = first_circuit.LookupParameter("Cable Tray ID").Id

# Creating of parameter string filter for electrical system
fnrvStr = FilterStringContains()
pvp = ParameterValueProvider(param_id)
frule = FilterStringRule(pvp, fnrvStr, search_str, True)
str_filter = ElementParameterFilter(frule)

el_sys = FilteredElementCollector(doc).\
	OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_ElectricalCircuit).\
	WhereElementIsNotElementType().\
	WherePasses(str_filter).\
	ToElements()

# Creation of multicategory filter
# # cat_list = [BuiltInCategory.OST_Rooms, BuiltInCategory.OST_Walls,
# cat_list = [BuiltInCategory.OST_Rooms, BuiltInCategory.OST_Walls, BuiltInCategory.OST_Windows, BuiltInCategory.OST_Doors]
# typed_list = List[BuiltInCategory](cat_list)
# multi_filter = ElementMulticategoryFilter(typed_list)

# output = FilteredElementCollector(doc).WherePasses(multi_filter).ToElements()

# uidoc.Selection.SetElementIds()

OUT = el_sys
