
import clr

# ================ Revit imports
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager


# ================ local imports
import toolsrvt
from toolsrvt import *

def get_location_by_element(_rvt_element): 
	# get connector location
	elem_connectors = _rvt_element.MEPModel.ConnectorManager.Connectors
	for con in elem_connectors:
		is_elec = con.Domain == Domain.DomainElectrical
		is_power = False
		if is_elec:
			is_power = con.ElectricalSystemType == Electrical.ElectricalSystemType.PowerCircuit
		if all([is_elec, is_power]):
			return con.Origin

def get_nearest_index_by_point(test_point, points):
	"""
		In a list of points, there is an ordered list of points. 
		The 'test_point' is very close to one of these points.
		Return the index number of the nearest point
	"""

	distances = [test_point.DistanceTo(pnt) for pnt in points]
	min_dist_index = distances.index(min(distances))
	return min_dist_index

def get_sorted_circuit_elements(_rvt_circuit: Electrical.ElectricalSystem):
	"""
		Return circuit elements, that are sorted by distance along circuit path
	"""

	rvt_elems = _rvt_circuit.Elements
	elems_location_point: list[XYZ] = [get_location_by_element(i) for i in rvt_elems]
	# find nearest point in path
	rvt_path = _rvt_circuit.GetCircuitPath()
	point_index = [get_nearest_index_by_point(pnt, rvt_path) for pnt in elems_location_point]
	sorted_pairs = sorted(zip(rvt_elems, point_index), key=lambda x: x[1])
	sorted_elements = [pair[0] for pair in sorted_pairs]
	return sorted_elements

def get_cable_name(el_sys):
	circuit_wire_size = el_sys.WireSizeString
	circuit_wire_type = el_sys.WireType.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()

	if "#2.5" in circuit_wire_size and "NYM" in circuit_wire_type:
		circuit_wire_str = "NYM 3x2.5"
	elif "#2.5" in circuit_wire_size and "NHXH E30" in circuit_wire_type:
		circuit_wire_str = "NHXH E30 3x2.5"
	elif "4" in circuit_wire_size and "NYM" in circuit_wire_type:
		circuit_wire_str = "NYM 3x4"
	elif "4" in circuit_wire_size and "NHXH E30" in circuit_wire_type:
		circuit_wire_str = "NHXH E30 3x4"
	else:
		circuit_wire_str = ""
	return circuit_wire_str
