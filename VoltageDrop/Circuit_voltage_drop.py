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


def get_current_at_point(_current, _count, _n_elems):
	current_sub = _current / _n_elems * _count
	point_current = _current - current_sub
	return point_current


def check_point(_point, _point_list):
	# type: (Autodesk.Revit.DB.XYZ, List[Autodesk.Revit.DB.XYZ]) -> bool

	"""Check if the point is allmost equqal to the points in list\n
		return:
			True: if point is near
			False: if point is not near
	"""
	for pnt in _point_list:
		dist = _point.DistanceTo(pnt)
		if dist < 0.01:
			# This point is near to one of the points
			return True
	return False


def get_points_lenght(_el_sys):
	# check if path mode set not to Farthest device.
	# else - change path to All Devices
	sys_path = _el_sys.GetCircuitPath()
	mode_farthest = Autodesk.Revit.DB.Electrical.ElectricalCircuitPathMode.FarthestDevice
	mode_all_devices = Autodesk.Revit.DB.Electrical.ElectricalCircuitPathMode.AllDevices
	path_mode = _el_sys.CircuitPathMode
	if path_mode == mode_farthest:
		_el_sys.CircuitPathMode = mode_all_devices
	el_sys_connectors = _el_sys.ConnectorManager.Connectors

	# filter out connector of electrical board
	board_id = _el_sys.BaseEquipment.Id
	connector_list = [i for i in el_sys_connectors
		if [x for x in i.AllRefs][0].Owner.Id != board_id]
	connector_points = [
		[x for x in i.AllRefs][0].Origin
		for i in connector_list]

	# calculate distance while point != point in connectors
	length_list = list()
	length_current = 0
	for i, pnt in enumerate(sys_path):
		# do not check last point
		if i == len(sys_path) - 1:
			break
		pnt_next = sys_path[i + 1]
		length_current += pnt.DistanceTo(pnt_next)
		if check_point(pnt_next, connector_points):
			length_list.append(length_current)
			length_current = 0
	return length_list


def calc_circuit_vd(_el_sys):
	"""Calculate voltage dorp from board to consumer (local).\n
		args:\n
			_el_sys - electrical system\n
			_est_current - estimated current\n
		return:\n
			voltage drop
	"""

	# ============== Voltage Drop Local ==============
	# EXAMPLE of caclulations
	# SEE: http://www.electricalaxis.com/2015/03/how-to-calculate-voltage-drop-of.html
	# find voltage drop to the next device.

	# system parameters
	# sys_board = _el_sys.BaseEquipment
	sys_elems = [i for i in _el_sys.Elements]
	n_elems = len(sys_elems)

	est_current = _el_sys.LookupParameter("E_EstCurrent").AsDouble()
	# create list that describes net.
	points_current = [
		get_current_at_point(est_current, i[0], n_elems)
		for i in enumerate(sys_elems)]

	points_lenght = get_points_lenght(_el_sys)
	points_info = zip(points_current, points_lenght)

	# get Z from the data base
	# calculate Vd using formulas
	# 1p: Vd = 2 * points_info[0] Z * points_info[1]
	# 3p: Vd = sqrt(3) * points_info[0] Z * points_info[1]

	return est_current, points_info
