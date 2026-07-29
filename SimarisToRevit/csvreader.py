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

def _parse_numeric_value(value: str, csv_delimiter: str = ';'):
    """Robust numeric parser that respects the CSV delimiter.
    
    When csv_delimiter == ';':
        . = thousands separator (remove), , = decimal (replace with .)
    Otherwise:
        , = thousands (remove), . = decimal
    """
    value = value.strip()
    if value == '-':
        return '-'
    if not value:
        return value

    original_value = value

    if csv_delimiter == ';':
        # European style (common with ; delimiter)
        value = value.replace('.', '')      # remove thousands separator
        value = value.replace(',', '.')     # decimal separator
    else:
        # Default / US style
        value = value.replace(' ', '')
        value = value.replace(',', '')      # thousands separator

    try:
        num = float(value)
        return int(num) if num == int(num) else num
    except ValueError:
        return original_value


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
    with open(csv_path, 'r', encoding='utf-8-sig') as file:
        lines = file.readlines()
    
    if not lines or not any(line.strip() for line in lines):
        raise ValueError("File is empty or contains no non-empty lines")
    
    # Step 3: Find the first non-empty line as header
    header_line = None
    header_index = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped:
            header_line = stripped
            header_index = i
            break
    if not header_line:
        raise ValueError("No non-empty lines found in file")
    
    # Step 4: Detect delimiter
    sample_content = ''.join(lines[header_index:header_index + 5])
    try:
        dialect = csv.Sniffer().sniff(sample_content)
        delimiter = dialect.delimiter
    except csv.Error:
        delimiter = None
    
    if not delimiter:
        possible_delimiters = [';']
        for delim in possible_delimiters:
            try:
                reader = csv.reader(io.StringIO(sample_content), delimiter=delim)
                next(reader)
                delimiter = delim
                break
            except csv.Error:
                continue
        if not delimiter:
            raise ValueError("Unable to detect delimiter - file may be malformed")
    
    # Parse header
    header_reader = csv.reader([header_line], delimiter=delimiter)
    header = next(header_reader)
    header = [field.strip().replace('\ufeff', '') for field in header]
    
    # Step 5: Validate required header fields
    required_fields = {
        "Designation", "Catalog reference",
        "In [A]", "IR [A]", "tR [s]",
        "Isd [A] undirected", "tsd [s] undirected",
        "Ii [A]", "Ig [A]", "tg [s]"
    }

    header_set = set(header)
    missing_fields = required_fields - header_set
    if missing_fields:
        raise ValueError(f"Wrong file format: Missing required header fields {list(missing_fields)}")
    
    string_fields = {"Designation", "Catalog reference"}
    numeric_fields = required_fields - string_fields
    
    # Step 6: Parse remaining rows
    data_lines = '\n'.join(lines[header_index + 1:])
    reader = csv.DictReader(io.StringIO(data_lines), fieldnames=header, delimiter=delimiter)
    
    # Step 7: Process rows
    result = []
    seen_designations = set()
    duplicate_designations = set()
    
    for row in reader:
        if not any(row.values()):
            continue
        
        cleaned_row = {}
        for key, value in row.items():
            if key not in required_fields:
                continue
            value = value.strip()
            
            if key in string_fields:
                cleaned_row[key] = value
            elif key in numeric_fields:
                cleaned_row[key] = _parse_numeric_value(value, delimiter)
        
        if 'Designation' not in cleaned_row or not cleaned_row['Designation']:
            continue
        
        designation = cleaned_row['Designation']
        if designation in seen_designations:
            duplicate_designations.add(designation)
        else:
            seen_designations.add(designation)
        
        result.append(cleaned_row)
    
    # Step 8: Check for duplicates
    if duplicate_designations:
        dup_list = ', '.join(f'"{dup}"' for dup in sorted(duplicate_designations))
        raise ValueError(f"Check csv info. Values are not unique: {dup_list}")
    
    if not result:
        raise ValueError("No valid data rows found after header")
    
    # Step 9: Convert to set of frozensets
    result_set = {frozenset(d.items()) for d in result}
    return result_set
