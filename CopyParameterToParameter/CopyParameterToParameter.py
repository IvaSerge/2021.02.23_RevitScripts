"""
Script copies parameter values from family to other family or list of families.
Families may be selected inside Dynamo or using API.
"""

import clr
import sys

dir_path = IN[0].DirectoryName  # type: ignore
sys.path.append(dir_path)


# ================ Revit imports
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# ================ Python imports
from System import Array
from System.Collections.Generic import *
from importlib import reload

# ================ local imports
import toolsrvt
reload(toolsrvt)
from toolsrvt import *

def get_elements_contains_parameter(_doc, _param_name):
	"""Get elements whose parameter with the given name has a value.

	args:
		_doc: active document
		_param_name (str): parameter name

	return:
		list of Autodesk.Revit.DB.Element
	"""

	parameter_id = [
		i for i in
		FilteredElementCollector(_doc).OfClass(ParameterElement)
		if i.Name == _param_name]
	if parameter_id:
		parameter_id = parameter_id[0].Id
	else:
		error_str = "Parameter not found: " + _param_name
		raise ValueError(error_str)

	has_value_rule = ParameterFilterRuleFactory.CreateHasValueParameterRule(
		parameter_id)
	parameter_filter = ElementParameterFilter(has_value_rule)

	elems = FilteredElementCollector(_doc).\
		WhereElementIsNotElementType().\
		WherePasses(parameter_filter).\
		ToElements()
	return elems

# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView
reload_var = IN[1]  # type: ignore
rvt_elem = IN[2]  # type: ignore
param_from = IN[3]  # type: ignore
param_to = IN[4]  # type: ignore

# Element selection
if rvt_elem:
	in_elements = [UnwrapElement(rvt_elem)]  # type: ignore
else:
	in_elements = [uidoc.Selection.PickObject(
		Autodesk.Revit.UI.Selection.ObjectType.Element,
		"Element selection")]

# param_from = "TSLA_SCOPE_ID"
# param_to = "TSLA_Shop"

# If all elements in the model needed
# in_elements = get_elements_contains_parameter(doc, param_from)

elem_param_list = list()
for elem in in_elements:
	param_val = toolsrvt.get_parval(
		elem,
		param_from)
	elem_param_list.append(
		[
			elem,
			param_val
		]
	)

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

for elem in elem_param_list:
	in_elem = elem[0]
	param_val = elem[1]
	try:
		toolsrvt.setup_param_value(
			in_elem,
			param_to,
			param_val)
	except:
		continue

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()


# OUT = in_elem, param_val
OUT = len(in_elem)
