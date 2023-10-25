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

import pandas as pd

# ================ local imports
import toolsrvt
reload(toolsrvt)
from toolsrvt import *


class BOQAnalyze():

	@staticmethod
	def get_boq_by_elements(elems_list):

		# BOQ schedule
		# | Category | Description |

		cat_list = [i.Category.Name for i in elems_list]

		return cat_list
