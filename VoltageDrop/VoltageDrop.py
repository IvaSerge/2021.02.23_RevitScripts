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


# ================ GLOBAL VARIABLES
global doc  # type: ignore
doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
app = uiapp.Application
DISTR_SYS_NAME = "230/400V"

reload = IN[1]  # type: ignore
panel_instance = UnwrapElement(IN[2])  # type: ignore
outlist = list()


# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# get Estimated Current of circuit
# get circuit path
# get ammount of consumers
# get number of poles

# ============== Voltage Drop Local ==============
# EXAMPLE of caclulations
# SEE: http://www.electricalaxis.com/2015/03/how-to-calculate-voltage-drop-of.html
# find voltage drop to the next device.
# create list that describes net.
# points_info = [(Estimated Current / n_of_consumers) * (n_of_consumers - coint)], [Length to point]
# type: points_info[Current, Lenght]
# get Z from the data base
# calculate Vd using formulas
# 1p: Vd = 2 * points_info[0] Z * points_info[1]
# 3p: Vd = sqrt(3) * points_info[0] Z * points_info[1]

# ============== Voltage Drop Owerall ==============
# find all the net from source to the current net.
# calculate Local voltage drop for every element of net
# Sum results

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = None
