# ================ system imports
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'

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


def calc_circuit_vd(_el_sys):
	"""Calculate voltage dorp from board to consumer (local).\n
		args:\n
			_el_sys - electrical system\n
		return:\n
			voltage drop
	"""

	# ============== Voltage Drop Local ==============
	# EXAMPLE of caclulations
	# SEE: http://www.electricalaxis.com/2015/03/how-to-calculate-voltage-drop-of.html
	# find voltage drop to the next device.
	pass
