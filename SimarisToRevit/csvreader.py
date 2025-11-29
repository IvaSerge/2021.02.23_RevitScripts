import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)


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

from pathlib import Path

import csv
import re
import os
import io

import toolsrvt

import csv
import os
import io  # For string-based sniffing if needed

def get_info_from_csv(csv_path):
    """
    Parses a CSV file, automatically detects the delimiter and thousands separator,
    validates the header (removing BOM if present), checks for unique "Designation" values,
    and returns a set of frozensets (each representing a frozen dictionary of element descriptions
    with their parameters). Raises errors for invalid formats, missing fields, or non-unique
    "Designation" values. For numeric fields, attempts conversion but keeps as string if it fails
    (including special handling for '-' as a placeholder).
    
    :param csv_path: Full path to the CSV file.
    :return: Set of frozensets, each frozenset is a frozen dict-like structure (e.g., frozenset([('Designation', 'value'), ...])).
    """
    
    # Step 1: Check if the file exists and is readable
    if not os.path.exists(csv_path) or not os.path.isfile(csv_path):
        raise FileNotFoundError(f"File not found or inaccessible: {csv_path}")
    
    # Step 2: Open the file and read all lines for processing
    with open(csv_path, 'r', encoding='utf-8-sig') as file:  # Use 'utf-8-sig' to automatically handle and remove BOM
        lines = file.readlines()
    
    # If no lines or all empty, raise an error
    if not lines or not any(line.strip() for line in lines):
        raise ValueError("File is empty or contains no non-empty lines")
    
    # Step 3: Find the first non-empty line as header
    header_line = None
    header_index = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped:  # First non-empty line
            header_line = stripped
            header_index = i
            break
    if not header_line:
        raise ValueError("No non-empty lines found in file")
    
    # Step 4: Detect delimiter using csv.Sniffer on the header line and a few following lines
    sample_content = ''.join(lines[header_index:header_index + 5])  # Sample header + up to 4 rows
    try:
        dialect = csv.Sniffer().sniff(sample_content)
        delimiter = dialect.delimiter
    except csv.Error:
        delimiter = None
    
    # Fallback: If sniffer fails, try common delimiters manually
    if not delimiter:
        possible_delimiters = [',', ';', '\t']
        for delim in possible_delimiters:
            try:
                reader = csv.reader(io.StringIO(sample_content), delimiter=delim)
                next(reader)  # Try to read header
                delimiter = delim
                break
            except csv.Error:
                continue
        if not delimiter:
            raise ValueError("Unable to detect delimiter - file may be malformed")
    
    # Parse the header using the detected delimiter
    header_reader = csv.reader([header_line], delimiter=delimiter)
    header = next(header_reader)
    # Clean whitespace and explicitly remove BOM (\ufeff) if present in any field
    header = [field.strip().replace('\ufeff', '') for field in header]
    
    # Step 5: Validate required header fields
    required_fields = {
        "Designation", "Catalog reference",
        "In [A]",
        "IR [A]", "tR [s]",
        "Isd [A] undirected", "tsd [s] undirected",
        "Ii [A]",
        "Ig [A]", "tg [s]"
    }

    header_set = set(header)
    missing_fields = required_fields - header_set
    if missing_fields:
        raise ValueError(f"Wrong file format: Missing required header fields {list(missing_fields)}")
    
    # Define string and numeric fields for type checking
    string_fields = {"Designation", "Catalog reference"}
    numeric_fields = required_fields - string_fields
    
    # Step 6: Parse the remaining rows (starting after header)
    # Join lines after header for csv.DictReader
    data_lines = '\n'.join(lines[header_index + 1:])
    reader = csv.DictReader(io.StringIO(data_lines), fieldnames=header, delimiter=delimiter)
    
    # Step 7: Process rows, handle thousands separators, and enforce types
    result = []  # Temporary list of dicts
    thousands_separators = [',', '.', ' ']  # Common ones to try removing
    seen_designations = set()  # To track unique Designations
    duplicate_designations = set()  # To collect duplicates
    
    for row in reader:
        if not any(row.values()):  # Skip empty rows
            continue
        
        cleaned_row = {}
        for key, value in row.items():
            if key not in required_fields:
                continue  # Ignore extra fields
            value = value.strip()
            
            if key in string_fields:
                cleaned_row[key] = value
            elif key in numeric_fields:
                if value == '-':
                    cleaned_row[key] = '-'  # Treat '-' as a special placeholder string
                    continue
                
                # Detect and remove thousands separator
                original_value = value
                for sep in thousands_separators:
                    if sep in value:
                        value = value.replace(sep, '')
                # Try to convert to float (allow decimals) or int; if fails, keep as string
                try:
                    cleaned_row[key] = float(value) if '.' in value else int(value)
                except ValueError:
                    cleaned_row[key] = original_value  # Keep the original stripped value as string
        
        # Check if Designation is present and non-empty
        if 'Designation' not in cleaned_row or not cleaned_row['Designation']:
            continue  # Skip rows without valid Designation
        
        # Check for uniqueness
        designation = cleaned_row['Designation']
        if designation in seen_designations:
            duplicate_designations.add(designation)
        else:
            seen_designations.add(designation)
        
        result.append(cleaned_row)
    
    # Step 8: Check for duplicates and raise if any
    if duplicate_designations:
        dup_list = ', '.join(f'"{dup}"' for dup in sorted(duplicate_designations))
        raise ValueError(f"Check csv info. Values are not unique: {dup_list}")
    
    # Step 9: Final check - ensure there is at least one valid row
    if not result:
        raise ValueError("No valid data rows found after header")
    
    # Step 10: Convert to set of frozensets for hashable uniqueness (since dicts are unhashable)
    result_set = set()
    for d in result:
        result_set.add(frozenset(d.items()))
    
    return result_set


# def get_breakers_info(csv_breakers):
# 	# type: (Path) -> list[str]
# 	"""Get parametrs of circuit breakers from csv

# 	args:
# 		csv_breakers - path to csv file
# 	return:
# 		cbreakers_list - list of settings
# 	"""

# 	cbreakers_list = list()
# 	re_circuit_number = re.compile(r"(?<=\[).*(?=\])")
# 	re_panel_name = re.compile(r".+(?=\[)")

# 	breaker_trips = {
# 		"3WL13634NG611AA2": "ETU76B",  # 5000A in substation
# 		"3WL12403NG611AA2": "ETU76B",  # 4000A in substation
# 		"3WL12323NG611AA2": "ETU76B",  # 3200A in substation
# 		"3WL11163NG611AA2": "ETU76B",  # 1600A in substation
# 		"3WL11163CB611AA2": "ETU25B",  # 1600A in distribution panel
# 		"3WA12204AF010AA0": "ETU600",  # 2000A
# 		"3VA27126AC010AA0": "ETU350",  # 1250A in tap-off Unit
# 		"3VA25106JP320AA0": "ETU550",  # 1000A
# 		"3VA24636KP320AA0": "ETU850",  # 630A
# 		"3VA24636HN320AA0": "ETU350",  # 630A in tap-off Unit
# 		"3VA23406KP320AA0": "ETU850",  # 400A
# 		"3VA23406HN320AA0": "ETU350",  # 400A in tap-off Unit
# 		"3VA22256KP320AA0": "ETU850",  # 250A
# 		"3VA22256HN320AA0": "ETU350",  # 250A in tap-off Unit
# 		"3VA21166KP320AA0": "ETU850",  # 160A
# 		"3VA21166HN320AA0": "ETU350",  # 160A in tap-off Unit 
# 		"3VA21105HN320AA0": "ETU350",  # 100As
# 		"Micrologic 6.0X": "Micrologic 6.0X",  # 1000A for Shnieder MCCB
# 	}

# 	with open(csv_breakers, mode='r', encoding='utf-8-sig') as csv_file:
# 		csv_reader = csv.reader(csv_file, delimiter=';', quoting=csv.QUOTE_MINIMAL)
# 		for row in csv_reader:
# 			breaker_parameters = list()
# 			# check if row is not empty
# 			if len(row) < 17:
# 				continue

# 			circuit_number = re_circuit_number.search(row[0])
# 			if circuit_number:
# 				circuit_number = circuit_number.group(0)

# 			panel_name = re_panel_name.search(row[0])
# 			if panel_name:
# 				panel_name: str = panel_name.group(0)

# 			breaker_parameters.append(panel_name)
# 			breaker_parameters.append(circuit_number)

# 			# add trip parameter
# 			breaker_type = row[1]
# 			breaker_trip = breaker_trips.get(breaker_type)
# 			if not breaker_trip:
# 				breaker_trip = "-"

# 			breaker_parameters.append(breaker_trip)
# 			breaker_parameters.extend(row[2:5])
# 			breaker_parameters.extend(row[6:8])
# 			breaker_parameters.append(row[15])
# 			breaker_parameters += row[17:]
# 			# Remove touthends separator
# 			breaker_parameters = [i.replace(".", "") if i else None for i in breaker_parameters]
# 			cbreakers_list.append(breaker_parameters)

# 	return cbreakers_list


# def csv_to_rvt_elements(csv_info, doc):
# 	param_toset_circuits = [
# 		"_Breaker_Type",
# 		"RBS_ELEC_CIRCUIT_FRAME_PARAM",
# 		"_IR(LTPU)",
# 		"_tr(LTD)",
# 		"_Isd(STPU)",
# 		"_tsd(STD)",
# 		"_Ii(INST)",
# 		"_Ig(GFPU)",
# 		"_tg(GFD)"]
# 	param_toset_panel = [
# 		"_Breaker_Type",
# 		"RBS_ELEC_PANEL_MCB_RATING_PARAM",
# 		"_IR(LTPU)",
# 		"_tr(LTD)",
# 		"_Isd(STPU)",
# 		"_tsd(STD)",
# 		"_Ii(INST)",
# 		"_Ig(GFPU)",
# 		"_tg(GFD)"]

# 	elem_list = list()
# 	for row in csv_info:
# 		panel_name = row[0]
# 		if not panel_name:
# 			# elem_list.append(None)
# 			continue

# 		circuit_number = int(row[1])
# 		panel_rvt = toolsrvt.inst_by_cat_strparamvalue(
# 			doc,
# 			BuiltInCategory.OST_ElectricalEquipment,
# 			BuiltInParameter.RBS_ELEC_PANEL_NAME,
# 			panel_name,
# 			False)
# 		# TODO: check if panel is not unique - write report
# 		# check panel name is equal to panel name
# 		try:
# 			panel_rvt = [i for i in panel_rvt if i.Name == panel_name][0]
# 		except:
# 			error_text = "Panel not found :" + panel_name
# 			print(error_text)
# 			raise ValueError(error_text)

# 		# "0" is main circuit breaker of the panel
# 		if circuit_number == 0:
# 			panels_list = [panel_rvt] * len(param_toset_panel)
# 			param_values = zip(panels_list, param_toset_panel, row[2:])
# 			elem_list.extend(param_values)

# 		# "%n" is branch circuit of the panel
# 		else:
# 			try:
# 				circutits_rvt = toolsrvt.elsys_by_brd(panel_rvt)[1]
# 			except:
# 				# circuit in Revit not fount. Panel is empty
# 				error_text = "Panel do not have branch circuits: " + panel_name
# 				print(error_text)
# 				raise ValueError(error_text)

# 			try:
# 				circutit_rvt = [i for i in circutits_rvt if i.StartSlot == circuit_number][0]
# 			except:
# 				# circuit in Simaris do not have analog in Revit model. Situation to be checked
# 				error_text = "Circuit not found :" + panel_name + ": " + str(circuit_number)
# 				print(error_text)
# 				raise ValueError(error_text)

# 			# check if circuit is not spare
# 			if circutit_rvt.CircuitType != Electrical.CircuitType.Circuit:
# 				# circuit is Spare - not possible to write parameters
# 				error_text = "Circuit is spare: " + panel_name + ": " + str(circuit_number)
# 				print(error_text)
# 				raise ValueError(error_text)

# 			circutit_list = [circutit_rvt] * len(param_toset_circuits)
# 			# change value for frame to represent Revit value
# 			display_units = doc.GetUnits().GetFormatOptions(Autodesk.Revit.DB.SpecTypeId.Current).GetUnitTypeId()
# 			values_list = row[2:]
# 			values_list[1] = Autodesk.Revit.DB.UnitUtils.ConvertToInternalUnits(float(values_list[1]), display_units)

# 			param_values = zip(circutit_list, param_toset_circuits, values_list)
# 			elem_list.extend(param_values)

# 	return elem_list
