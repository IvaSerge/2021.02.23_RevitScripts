"""
Script copies parameters from circuints in old model to circuits in new model.
Why?
Parameter was removed incedently and synced in new model.
Info need to be restored from old model from local storage.
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


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView
reload_var = IN[1]  # type: ignore

outlist = []

# be sure, that there is only one old document is open
docs = uiapp.Application.Documents
doc_old = [i for i in docs if i != doc][0]

# get all electrical circuits in old document
circuits_old = FilteredElementCollector(doc_old).\
	OfCategory(BuiltInCategory.OST_ElectricalCircuit).\
	WhereElementIsNotElementType()

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

for circuit_old in circuits_old:
	# find the same electrical new_circuit by Id in new document
	id_old = circuit_old.Id

	circuit_new = doc.GetElement(id_old)
	if not circuit_new:
		continue

	# read old_parameter
	param_value = toolsrvt.get_parval(circuit_old, "Cable Description")
	if not param_value:
		continue

	toolsrvt.setup_param_value(circuit_new, "Cable Description", param_value)

	outlist.append(circuit_new)

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = outlist
