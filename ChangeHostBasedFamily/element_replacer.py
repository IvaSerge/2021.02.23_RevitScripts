import clr
import os
import sys

# ================ Revit imports
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *
from Autodesk.Revit.Exceptions import InvalidOperationException

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

import System
from System import Array
from System.Collections.Generic import *

# ================ local imports
import toolsrvt

import math
import scipy
from scipy.spatial.transform import Rotation

class ElementReplacer:
	"""
		Class represents Family instance that will replace existing family instance
	"""

	# class properties
	doc = None

	def __init__(self, _old_instance):
		self.old_instance: FamilyInstance = _old_instance
		self.new_type: FamilyType = None
		self.new_inst: FamilyInstance = None
		self.tags_list: list[IndependentTag]
		self.param_list = []
		self.el_sys: Electrical.ElectricalSystem = None
		self.rotation = float()

	def get_element_tags(self):
		doc: Document = self.doc
		elem_bic = self.old_instance.Category.BuiltInCategory
		tag_collector = FilteredElementCollector(doc).OfClass(IndependentTag).WhereElementIsNotElementType().ToElements()
		target_element_id = self.old_instance.Id

		tags_associated_with_element = []
		for tag in tag_collector:
			tag_hosts_ids = [i.HostElementId for i in tag.GetTaggedElementIds()]
			if target_element_id in tag_hosts_ids:
				tags_associated_with_element.append(tag)
		self.tags_list = tags_associated_with_element


	def create_new_instance(self):
		doc: Document = self.doc
		new_type: FamilyType = self.new_type
		family_inst = None
		
		# create family instance based on lication point
		ins_pnt = self.old_instance.Location.Point
		# host
		host_lvl_Id = toolsrvt.get_parval(self.old_instance, "INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM")
		rvt_host_lvl = doc.GetElement(host_lvl_Id)

		if not new_type.IsActive:
			new_type.Activate()
			doc.Regenerate()

		family_inst = doc.Create.NewFamilyInstance(
			ins_pnt,
			new_type,
			rvt_host_lvl,
			Structure.StructuralType.NonStructural)
		doc.Regenerate()
		self.new_inst = family_inst

	def rotate_inst(self):
		doc = self.doc
		old_transform = self.old_instance.GetTotalTransform()
		x_axis = old_transform.BasisX
		y_axis = old_transform.BasisY
		z_axis = old_transform.BasisZ

		rotation_matrix = [
			[round(x_axis.X, 5), round(x_axis.Y, 5), round(x_axis.Z, 5)],
			[round(y_axis.X, 5), round(y_axis.Y, 5), round(y_axis.Z, 5)],
			[round(z_axis.X, 5), round(z_axis.Y, 5), round(z_axis.Z, 5)],
		]

		angles = ElementReplacer.euler_angles_from_rotation_matrix(rotation_matrix)
		self.rotation = float(angles[0])


	def switch_tags(self):
		for tag in self.tags_list:  # Assuming self.tags_list is List[IndependentTag]
			# Remove old reference
			old_ref_list = tag.GetTaggedReferences()
			old_ref = old_ref_list[0]
			tag_visible = tag.IsLeaderVisible(old_ref)
			tag_end_condition = tag.LeaderEndCondition
			try:
				tag_elbow = tag.GetLeaderElbow(old_ref)
			except:
				tag_elbow = None

			if tag_end_condition == LeaderEndCondition.Free and tag_visible:
				tag_end = tag.GetLeaderEnd(old_ref)
			else:
				tag_end = None
			tag.RemoveReferences(old_ref_list)
	
			# Add reference
			new_ref = Reference(self.new_inst)
			new_ref_list = [new_ref]
			tag.AddReferences(new_ref_list)
			if tag_elbow:
				tag.SetLeaderElbow(new_ref, tag_elbow)
			if tag_end:
				tag.SetLeaderEnd(new_ref, tag_end)

	def get_parameters(self):
		# chec if readonly and value exists
		param_list = []
		old_inst = self.old_instance
		for param in old_inst.GetOrderedParameters():
			p_has_value = param.HasValue
			p_read_only = param.IsReadOnly
			p_Id = param.Id
			# p_modifiable = param.UserModifiable
			is_valid = all([p_has_value, not(p_read_only)])
			
			if not is_valid:
				continue
			
			# additional parameter filters
			# Elevation from level
			param_ids_to_ignore = [
					-1001352,  # Level
					-1002062,  # Level
					-1001360,  # Elevation from Level
					-1001363,  # Host
					-1002108,  # Host Id
					-1001364,  # Offset from Host
				]
			# ignore level and offset parameters
			if p_Id in param_ids_to_ignore:
				continue

			p_name = param.Definition.Name
			p_value = toolsrvt.get_parval(old_inst, p_name)
			if p_value is not None and p_value != "":
				param_list.append([p_name, p_value])

		self.param_list = param_list
	
	def get_level_and_elevation(self):
		old_inst = self.old_instance
		level_params = []
		# get param level and drop error if not found
		shedule_lvl_id = toolsrvt.get_parval(old_inst, "INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM")
		if not shedule_lvl_id:
			error_text = f"Level not found. Check instance: {str(old_inst.Id.IntegerValue)}"
			print(error_text)
			raise ValueError(error_text)

		elevation = toolsrvt.get_parval(old_inst, "INSTANCE_ELEVATION_PARAM")
		level_params.append(["INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM", shedule_lvl_id])
		level_params.append(["INSTANCE_ELEVATION_PARAM", elevation])

		# self.old_instance
		self.param_list.extend(level_params)

	def set_parameters(self):
		new_inst = self.new_inst
		param_list = self.param_list
		for param in param_list:
			p_name = param[0]
			p_value = param[1]
			try:
				toolsrvt.setup_param_value(new_inst, p_name, p_value)
			except:
				continue
		# set phase
		new_inst.CreatedPhaseId = self.old_instance.CreatedPhaseId

		# there is no Workset in standalone model.
		if hasattr(self.old_instance, "WorksetId"):
			workset_id = self.old_instance.WorksetId.IntegerValue
			toolsrvt.setup_param_value(new_inst, "ELEM_PARTITION_PARAM", int(workset_id))

	def get_el_sys(self):
		old_inst = self.old_instance
		old_elsystems = old_inst.MEPModel.GetElectricalSystems()
		if old_elsystems:
			all_sys = [i for i in old_elsystems]
		else:
			return None
		self.el_sys = all_sys


	def assign_el_sys(self):
		new_inst = self.new_inst
		doc = new_inst.Document
		el_systems = self.el_sys
		if not el_systems:
			return None

		connectors = new_inst.MEPModel.ConnectorManager.UnusedConnectors
		con_list = list(iter(connectors))
		sorted_con_list = sorted(con_list, key=lambda x: x.Description)
		zipped_systems = zip(el_systems, sorted_con_list)
	
		for zip_system in zipped_systems:
			el_system = zip_system[0]
			con = zip_system[1]
			con_set: ConnectorSet = ConnectorSet()
			con_set.Insert(con)
			el_system.Add(con_set)

	@staticmethod
	def euler_angles_from_rotation_matrix(rotation_matrix):
		r =  Rotation.from_matrix(rotation_matrix)
		angles = r.as_euler("zyx",degrees=True)
		return angles
