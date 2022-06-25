
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

el_systems = FilteredElementCollector(doc).\
	OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_ElectricalCircuit).\
	WhereElementIsNotElementType().\
	WherePasses(str_filter).\
	ToElements()

# Find first element
if el_systems:
	el_sys = el_systems[0]
	elements = [i for i in el_sys.Elements]
	if elements:
		first_elem = elements[0]
		first_elem_lst = [elements[0].Id]
		elem_collection = List[ElementId](first_elem_lst)
		uidoc.Selection.SetElementIds(elem_collection)
	else:
		first_elem = None
else:
	first_elem = None

OUT = first_elem, el_systems
