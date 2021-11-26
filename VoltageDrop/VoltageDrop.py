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

# ================ Python imports
import math
from math import sqrt

# ================ Local imports
import Circuit_voltage_drop
from Circuit_voltage_drop import calc_circuit_vd

# ================ GLOBAL VARIABLES
global doc  # type: ignore
doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
app = uiapp.Application
DISTR_SYS_NAME = "230/400V"

# find and set distribution system
testParam = BuiltInParameter.SYMBOL_NAME_PARAM
pvp = ParameterValueProvider(ElementId(int(testParam)))
fnrvStr = FilterStringEquals()
filter = ElementParameterFilter(
	FilterStringRule(pvp, fnrvStr, DISTR_SYS_NAME, False))

distrSys = FilteredElementCollector(doc).\
	OfCategory(BuiltInCategory.OST_ElecDistributionSys).\
	WhereElementIsElementType().\
	WherePasses(filter).\
	ToElements()[0].Id

reload = IN[1]  # type: ignore
el_instance = UnwrapElement(IN[2])  # type: ignore
outlist = list()

# get circuits
sys_type = Autodesk.Revit.DB.Electrical.ElectricalSystemType.PowerCircuit
# el_circuits = panel_instance.MEPModel.ElectricalSystems
el_circuits = el_instance.MEPModel.ElectricalSystems
el_circuit = [i for i in el_circuits if i.SystemType == sys_type][0]

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

sys_vd = calc_circuit_vd(el_circuit)

# ============== Voltage Drop Owerall ==============
# find all the net from source to the current net.
# calculate Local voltage drop for every element of net
# Sum results

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = sys_vd
