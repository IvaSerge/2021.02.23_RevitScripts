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
import csv
import os
import io


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
