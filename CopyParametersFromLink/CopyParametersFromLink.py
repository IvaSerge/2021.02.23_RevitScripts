import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
sys.path.append(IN[0].DirectoryName)  # type: ignore

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
			value = param.AsInteger()
		elif storeType == StorageType.Double:
			value = param.AsDouble()
		elif storeType == StorageType.ElementId:
			value = param.AsValueString()
	except:
		pass
	return value


def setup_param_value(elem, name, pValue):

	# check element staus
	elem_status = WorksharingUtils.GetCheckoutStatus(doc, elem.Id)

	if elem_status == CheckoutStatus.OwnedByOtherUser:
		return None

	# custom parameter
	param = elem.LookupParameter(name)
	# check is it a BuiltIn parameter if not found
	if not(param):
		try:
			param = elem.get_Parameter(get_bip(name)).Set(pValue)
		except:
			pass

	if param:
		try:
			param.Set(pValue)
		except:
			pass
	return elem


def get_bip(paramName):
	builtInParams = System.Enum.GetValues(BuiltInParameter)
	param = []
	for i in builtInParams:
		if i.ToString() == paramName:
			param.append(i)
			return i


def get_info(_elem_link, _elem, _param_list):
	search_list = zip([_elem_link] * len(_param_list), _param_list)
	found_list = [[
		_elem,
		i[1],
		get_parval(i[0], i[1])] for i in search_list]
	return found_list


doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView

reload = IN[1]  # type: ignore
calc_all = IN[2]  # type: ignore

params_dat = [
	"st_devicetag",
	"st_devicetag (NEW)",
	"st_Voltage",
	"st_Number of Poles",
	"st_Apparent Load",
	"st_connection_details",
	"st_FLA",
	"Comments",
	"TSLA_SCOPE_ID",
	"st_neutral",
	"INSTANCE_FREE_HOST_OFFSET_PARAM"
]

# Select element in current doc
sel_elem = uidoc.Selection.PickObject(Autodesk.Revit.UI.Selection.ObjectType.Element, "")
elem = doc.GetElement(sel_elem.ElementId)

# Select element in link
ref_elem_linked = uidoc.Selection.PickObject(Autodesk.Revit.UI.Selection.ObjectType.LinkedElement, "")
elem_ref = doc.GetElement(ref_elem_linked.ElementId)
doc_linked = elem_ref.GetLinkDocument()
elem_linked = doc_linked.GetElement(ref_elem_linked.LinkedElementId)

# get parameters from the linked element
info_list = get_info(elem_linked, elem, params_dat)

# get electrical circuit of element
# TODO Update for electircal panels


if elem.MEPModel.GetElectricalSystems():
	el_sys = list(elem.MEPModel.GetElectricalSystems())
	el_sys = el_sys[0]
else:
	el_sys = None

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# write parameters to main element
for i in info_list:
	setup_param_value(i[0], i[1], i[2])

# write parameters to circuit
if el_sys:
	el_sys.get_Parameter(BuiltInParameter.RBS_ELEC_CIRCUIT_NAME).Set(info_list[1][2])
	el_sys.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set(info_list[6][2])

TransactionManager.Instance.TransactionTaskDone()
# =========End transaction

OUT = info_list
