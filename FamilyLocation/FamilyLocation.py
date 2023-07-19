
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

clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

# ================ Python imports
import importlib
import toolsrvt
importlib.reload(toolsrvt)

import itertools
from itertools import groupby


def get_name(i):
	return i.Name


def get_name_param(i):
	return i.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()


def group_func(i):
	return i[0]


def get_types_by_family(_family):
	doc = _family.Document
	type_ids = _family.GetFamilySymbolIds()
	types_rvt = [doc.GetElement(i) for i in type_ids]
	types_sorted = sorted(types_rvt, key=get_name_param)
	family_lst = [_family] * len(types_sorted)
	return zip(family_lst, types_sorted)


global doc
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView

reload = IN[1]  # type: ignore
categories_lst = IN[2]  # type: ignore

pt_X_start = 50000
pt_Y_start = 50000
pt_Z_start = 0

# get category
categories_rvt = [toolsrvt.category_by_bic_name(doc, cat) for cat in categories_lst]

families_rvt = list()
# get all families of category and sort by Name
for cat in categories_rvt:
	bic = cat.Id
	families_all = FilteredElementCollector(doc).OfClass(Family).ToElements()
	families_by_cat = [i for i in families_all if i.FamilyCategory.Id == bic]
	families_sorted = sorted(families_by_cat, key=get_name)
	families_rvt.extend(families_sorted)

# for all families find all types. Create a list [family, type]
family_type_list = list()
for fam in families_rvt:
	types_lst = get_types_by_family(fam)
	family_type_list.extend(types_lst)

pt_X = pt_X_start
pt_Z = pt_Z_start
type_location = list()
for key, iter_items in groupby(family_type_list, key=group_func):
	for i, item in enumerate(iter_items):
		pt_Y = pt_Y_start + i * 2000
		location = [pt_X, pt_Y, pt_Z]
		type_location.append([item[1], location])

	pt_Y = pt_Y_start
	pt_Z += 500
	pt_X += 2500

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# Create instance of the type


# =========End transaction
TransactionManager.Instance.TransactionTaskDone()


points_lst = [Point.ByCoordinates(i[1][0], i[1][1], i[1][2]) for i in type_location]
OUT = points_lst
