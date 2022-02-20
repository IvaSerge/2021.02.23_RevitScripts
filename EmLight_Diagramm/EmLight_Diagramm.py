
from this import d
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

clr.AddReferenceByName('Microsoft.Office.Interop.Excel, Version=11.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c')
from Microsoft.Office.Interop import Excel  # type: ignore

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


def getByCatAndStrParam(_bic, _bip, _val, _isType):
	global doc
	if _isType:
		fnrvStr = FilterStringEquals()
		pvp = ParameterValueProvider(ElementId(int(_bip)))
		frule = FilterStringRule(pvp, fnrvStr, _val, False)
		filter = ElementParameterFilter(frule)
		elem = FilteredElementCollector(doc).\
			OfCategory(_bic).\
			WhereElementIsElementType().\
			WherePasses(filter).\
			ToElements()
	else:
		fnrvStr = FilterStringEquals()
		pvp = ParameterValueProvider(ElementId(int(_bip)))
		frule = FilterStringRule(pvp, fnrvStr, _val, False)
		filter = ElementParameterFilter(frule)
		elem = FilteredElementCollector(doc).\
			OfCategory(_bic).\
			WhereElementIsNotElementType().\
			WherePasses(filter).\
			ToElements()
	return elem


global doc
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView


board_inst = UnwrapElement(IN[3])  # type: ignore

# select view for diagramm
view_name = IN[2]  # type: ignore
view_diagramm = getByCatAndStrParam(
	BuiltInCategory.OST_Views,
	BuiltInParameter.VIEW_NAME,
	view_name,
	False)[0]

# type to install
type_emergency = getByCatAndStrParam(
	BuiltInCategory.OST_DetailComponents,
	BuiltInParameter.SYMBOL_NAME_PARAM,
	"2D_diagramm_E01",
	True)[0]

type_exit = getByCatAndStrParam(
	BuiltInCategory.OST_DetailComponents,
	BuiltInParameter.SYMBOL_NAME_PARAM,
	"2D_diagramm_E01",
	True)[0]


# for circuit in boards:
# find all elements by "Panel" and "Circuit Number"

# read element parameters
# convert parameters

# list [type, list[param, value]]

# insert 2D on drawing, add parameters


# # =========Start transaction
# TransactionManager.Instance.EnsureInTransaction(doc)

# # Start point
# start_pnt = XYZ(0, 0, 0)

# view_inst = doc.Create.NewFamilyInstance(
# 	start_pnt,
# 	symbol_type,
# 	view_diagramm)

# # =========End transaction
# TransactionManager.Instance.TransactionTaskDone()


OUT = symbol_type
