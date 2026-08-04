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
from typing import List

# ================ local imports
import toolsrvt
reload(toolsrvt)
from toolsrvt import *

import csvreader
reload(csvreader)

import circuit_breaker
reload(circuit_breaker)
from circuit_breaker import CircuitBreaker


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument

reload_IN = IN[1]  # type: ignore
csv_path = dir_path + "\\" + IN[2]  # type: ignore
outlist = list()
CircuitBreaker.doc = doc

# ================ get info for circuit breaker settings
settings_from_csv = csvreader.get_info_from_csv(csv_path)

breakers_list = [] 
error_list = []
for breaker_settings in settings_from_csv:
	try:
		circuit_breaker = CircuitBreaker(breaker_settings)
		breakers_list.append(circuit_breaker)
		print(circuit_breaker.revit_element.Id)
		print(circuit_breaker.params_list)
	except Exception as e:
		error_sting = str(e)
		error_list.append(error_sting)

try:
	# =========Start transaction
	TransactionManager.Instance.EnsureInTransaction(doc)

	# ================ set parameters
	for br in breakers_list:
		breaker = br # type: CircuitBreaker
		breaker.set_rvt_parameters()

	# =========End transaction
finally:
	TransactionManager.Instance.TransactionTaskDone()

OUT = [[i.revit_element, i.params_list] for i in breakers_list], error_list

