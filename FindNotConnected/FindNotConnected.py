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


def get_parval(elem, name):
	"""Get parametr value

	args:
		elem - family instance or type
		name - parameter name
	return:
		value - parameter value
	"""

	value = None
	# custom parameter
	param = elem.LookupParameter(name)
	# check is it a BuiltIn parameter if not found
	if not(param):
		param = elem.get_Parameter(get_bip(name))

	# get paremeter Value if found
	try:
		storeType = param.StorageType
		# value = storeType
		if storeType == StorageType.String:
			value = param.AsString()
		elif storeType == StorageType.Integer:
			value = param.AsDouble()
		elif storeType == StorageType.Double:
			value = param.AsDouble()
		elif storeType == StorageType.ElementId:
			value = param.AsValueString()
	except:
		pass
	return value


def get_bip(paramName):
	builtInParams = System.Enum.GetValues(BuiltInParameter)
	param = []
	for i in builtInParams:
		if i.ToString() == paramName:
			param.append(i)
			return i


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
	el_sys = lighting.MEPModel.ElectricalSystems

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

	if not(emerg_panel):
		outlist.append(lighting.Id.ToString())

# # =========Start transaction
# TransactionManager.Instance.EnsureInTransaction(doc)

# brd_updated = map(update_subboard_name, elemList)

# TransactionManager.Instance.TransactionTaskDone()
# # =========End transaction

OUT = outlist
