
import sys
sys.path.append(r"C:\Users\sivasiuk\AppData\Local\python-3.9.12-embed-amd64\Lib\site-packages")
sys.path.append(r"C:\Users\sivasiuk\AppData\Local\python-3.9.12-embed-amd64\Lib\site-packages\win32")
sys.path.append(r"C:\Users\sivasiuk\AppData\Local\python-3.9.12-embed-amd64\Lib\site-packages\win32\lib")

import win32com.client

def get_acad_instance():
	prog_ids = [
		"AutoCAD.Application.24.2",  # AutoCAD 2024
		"AutoCAD.Application.24.1",  # AutoCAD 2023
		"AutoCAD.Application"        # General AutoCAD ProgID
	]

	# Attempt to get the active AutoCAD instance by trying each ProgID
	for prog_id in prog_ids:
		try:
			acad_app = win32com.client.Dispatch(prog_id)
			print(f"Connected to AutoCAD via {prog_id}")
			return acad_app
		except Exception as e:
			error_string = f"Failed to connect with {prog_id}: {str(e)}"
			print(error_string)
			raise ValueError(error_string)

def get_active_document(acad_app):
	try:
		# Get the active document
		return acad_app.ActiveDocument
	except Exception as e:
		error_string = f"Failed to get active document: {str(e)}"
		print(error_string)
		raise ValueError(error_string)

def get_all_layers(doc):
	layers = doc.Layers  # Get the Layers collection
	layer_names = [layers.Item(i).Name for i in range(layers.Count)]
	return layer_names

def freeze_layer(doc, layer_name):
	layers = doc.Layers
	layer = layers.Item(layer_name)
	layer.Freeze = True

def unlock_layers(doc):
	"""Unlocks all locked layers in the given AutoCAD document."""
	layers = doc.Layers  # Get all layers
	for layer in layers:
		if layer.Lock:  # Check if layer is locked
			layer.Lock = False  # Unlock layer

def on_layers(doc):
	"""Turn on hidden layers in the given AutoCAD document."""
	layers = doc.Layers  # Get all layers
	for layer in layers:
		if not layer.LayerOn:  # Check if layer is on
			layer.LayerOn = True  # Turn layer on

def burst_block(doc, block_name):
	for entity in doc.ModelSpace:
		if entity.ObjectName == "AcDbBlockReference" and entity.Name == block_name:
			attributes = {}

			# Extract attribute values, positions, height, and style
			for attr in entity.GetAttributes():
				attributes[attr.TagString] = {
					"text": attr.TextString,
					"position": attr.InsertionPoint,
					"height": attr.Height,  # Copy text size
					"style": attr.StyleName  # Copy text style
				}

			# Explode the block
			exploded_objects = entity.Explode()
				
			# Replace attributes with MText at the correct position
			for obj in exploded_objects:
				if obj.ObjectName == "AcDbText" and obj.TextString in attributes:
					attr_data = attributes[obj.TextString]  # Get attribute data
						
					# Create a new MText object at the attribute's position
					mtext = doc.ModelSpace.AddMText(attr_data["position"], 10, attr_data["text"])  # Width 10 (adjustable)

					# Apply the original attribute's size and style
					mtext.Height = attr_data["height"]
					mtext.StyleName = attr_data["style"]

					# Remove the original exploded text
					obj.Delete()

def get_selection(doc):
	"""Prompts the user to select objects and prints their types."""
	outlist = []
	try:
		doc.SelectionSets.Item("TempSelection").Delete()
	except: pass

	try:
		selection_set = doc.SelectionSets.Add("TempSelection")  # Create temporary selection set
		selection_set.SelectOnScreen()  # Prompt user to select objects
		
		if selection_set.Count == 0:
			print("No objects selected.")
			return None

		for obj in selection_set:
			obj_type_str = f"Object Type: {obj.ObjectName}"
			print(obj_type_str)  # Prints object type
			obj_info = {
				"obj": obj,  # Object reference
				"obj_type": obj.ObjectName  # Object type string
			}
			outlist.append(obj_info)

		return outlist  # Return selection if needed

	except Exception as e:
		print(f"Error selecting objects: {e}")
		return None

	finally:
		# Cleanup: Delete selection set to prevent errors
		if "TempSelection" in doc.SelectionSets:
			doc.SelectionSets.Item("TempSelection").Delete()

def block_all_to_layer_null(doc, block_name_str):
	"""Moves all objects inside a block definition to layer '0' and sets color/lineweight to 'ByBlock'"""

	db = doc.Database
	block_table = db.Blocks
	block_info = []

	block_def = block_table.Item(block_name_str)
	for i in range(block_def.count):
		entity = block_def.Item(i)
		entity.Layer = "0"  # Move to layer "0"
		entity.Color = 0  # 0 = "ByBlock"
		entity.LineWeight = -1  # -1 = "ByBlock"
	doc.Regen(1)  # Refresh the active viewport to update changes
	return block_info

def get_visible_hatches(doc):
	visible_hatches = []

	mod_space = doc.ModelSpace.Count
	
	# # Iterate through all objects in ModelSpace
	# for entity in doc.ModelSpace:
	# 	if entity.ObjectName == "AcDbHatch" and entity.Visible:
	# 		visible_hatches.append(entity)
	
	return mod_space
