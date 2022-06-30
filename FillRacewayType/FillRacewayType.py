
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


def get_first_elem_of_system(_el_sys):
	"""Get first family instances of electrical system

		args:
		_el_sy: Electrical system

		return:
		Family instance
	"""
	first_elem = None
	elements = [i for i in _el_sys.Elements]
	if elements:
		first_elem = elements[0]

	return first_elem


def inst_by_cat_strparamvalue(_bic, _bip, _val, _isType):
	"""Get all family instances by category and parameter value

		args:
		_bic: BuiltInCategory.OST_xxx
		_bip: BuiltInParameter

		return:
		list()[Autodesk.Revit.DB.FamilySymbol]
	"""
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


def get_first_ref(_inst):
	conectors = _inst.MEPModel.ConnectorManager.Connectors
	if not conectors:
		return None

	for con in conectors:
		con_neibor = [i for i in con.AllRefs]
		if con_neibor:
			return con_neibor[0].Owner
	return None


global doc
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView

reload = IN[1]  # type: ignore
outlist = list()

cab_fitting_cat = BuiltInCategory.OST_CableTrayFitting
param_id = 79571

cab_fittings = inst_by_cat_strparamvalue(cab_fitting_cat, param_id, "", False)

neighbors = [get_first_ref(i) for i in cab_fittings]


OUT = zip(cab_fittings, neighbors)
