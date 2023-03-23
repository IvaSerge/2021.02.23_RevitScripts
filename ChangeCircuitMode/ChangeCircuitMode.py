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


def get_all_systems():
	"""
	Get all systems, that connected to electrical boards
	"""

	# Get all systems in project
	not_filtered_systems = FilteredElementCollector(doc).\
		OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_ElectricalCircuit).\
		WhereElementIsNotElementType().\
		ToElements()

	# filter out not connected systems
	all_systems = [sys for sys in not_filtered_systems if sys.BaseEquipment]

	# filter systems with NA parameter
	na_systems = [sys for sys in all_systems
		if "NA" == sys.LookupParameter("Cable Tray ID").AsString()]

	return na_systems


global doc
doc = DocumentManager.Instance.CurrentDBDocument
path_mode_all = Autodesk.Revit.DB.Electrical.ElectricalCircuitPathMode.AllDevices

systems_to_change = get_all_systems()

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

for el_sys in systems_to_change:
	elem_status = WorksharingUtils.GetCheckoutStatus(doc, el_sys.Id)
	if elem_status == CheckoutStatus.OwnedByOtherUser:
		continue

	el_sys.CircuitPathMode = path_mode_all

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = get_all_systems()
