import clr
import os
import sys

local_data = os.getenv("LOCALAPPDATA")
dyn_path = r"\python-3.9.12-embed-amd64\Lib"
py_path = local_data + dyn_path
sys.path.append(py_path)


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


def get_boq_by_elements(elems_list):

	# BOQ schedule
	# | Category | Description |
	elem_id = [i.Id.IntegerValue for i in elems_list]
	elem_categories = [i.Category.Name for i in elems_list]
	elem_description = [
		toolsrvt.get_parval(i.Symbol, "ALL_MODEL_DESCRIPTION")
		for i in elems_list]

	pd_elem_ids = pd.Series(elem_id)
	pd_cats = pd.Series(elem_categories)
	pd_des = pd.Series(elem_description)

	pd_elems_frame = pd.DataFrame({
		"Element Id": pd_elem_ids,
		"Category": pd_cats,
		"Description": pd_des})

	return pd_elems_frame.groupby(["Category", "Description"]).count()
