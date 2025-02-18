import sys
sys.path.append(r"C:\Users\sivasiuk\AppData\Local\python-3.9.12-embed-amd64\Lib\site-packages")
sys.path.append(r"C:\Users\sivasiuk\AppData\Local\python-3.9.12-embed-amd64\Lib\site-packages\win32")
sys.path.append(r"C:\Users\sivasiuk\AppData\Local\python-3.9.12-embed-amd64\Lib\site-packages\win32\lib")

import clr
import System
import win32
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
			print(f"Failed to connect with {prog_id}: {str(e)}")
	
	return None

def get_active_document(acad_app):
	try:
		# Get the active document
		return acad_app.ActiveDocument
	except Exception as e:
		print(f"Failed to get active document: {str(e)}")
		return None

# Example usage
acad_instance = get_acad_instance()
if acad_instance:
	doc = get_active_document(acad_instance)
	if doc:
		print(f"Active document: {doc.Name}")
	else:
		print("No active document found.")
else:
	print("AutoCAD instance not found.")

	
