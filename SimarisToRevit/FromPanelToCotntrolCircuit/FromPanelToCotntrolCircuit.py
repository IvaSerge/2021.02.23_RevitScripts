import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

dir_path = IN[0].DirectoryName  # type: ignore
sys.path.append(dir_path)


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

# ================ Python imports
import System
from System import Array
from System.Collections.Generic import *

import importlib
from importlib import reload

import csv
import re

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

reload_IN = IN[1]  # type: ignore
outlist = list()

# ================ get info for circuit breaker settings


# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# ================ set parameters


# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = None
