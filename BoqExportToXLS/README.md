

<!-- TABLE OF CONTENTS -->
<details open>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-script">About the script</a>
    </li>
    <li>
      <a href="#installation-of-python-modules">Installation of Python modules</a>
      <ul>
        <li><a href="#pip-installation">pip installation</a></li>
        <li><a href="#installation-of-python-modules">Installation</a></li>
      </ul>
    </li>
    <li><a href="#settings-in-revit">Settings in Revit</a></li>
    <li><a href="#excel-template">Excel template</a></li>
    <li><a href ="#data-base-access">Data base access</a></li>
    <li>
      <a href="#run-script-in-dynamo">Run script in Dynamo</a>
      <ul>
        <li><a href="#set-boq-name-and-parameters-manually">Set BOQ name and parameters manually</a></li>
        <li><a href="#set-boq-name-by-info-from-sql-database">Set BOQ name by info from SQL database</a></li>
      <ul>
    </li>
  </ol>
</details>

# About the script
The script generates a Bill of Quantities (BOQ) in both Excel and PDF formats.
File names are automatically generated using the company's naming convention.
There is no need for additional manual export of Revit schedules.

The script populates the first page based on the current Revit revision.  
The second page contains a list of pages affected by the change.  
The third page contains a list of materials, including specific items such as
IT RJ45 Jacks and Patch cords, that cannot be calculated within Revit.

**WARNING**
Still very specific families, like "busbars" of families,
that are not from company standard BIM catalogue, may not be calculated correctly.

# Installation of Python modules
Before script run, be sure that all necessary Python modules were installed.

## **pip** installation
To install modules in Dynamo Python please check this link:
[pip install guide](https://github.com/DynamoDS/Dynamo/wiki/Customizing-Dynamo's-Python-3-installation)

**NOTE**
Revit 2023 use Python v.3.9.12  
During installation, the following Python path must be utilized:  
`%LocalAppData%\python-3.9.12-embed-amd64`

## Installation of python modules
  - pip install pandas
  - pip install Pillow
  - pip inatall -U pypiwin32
  - pip inatall -U python-dotenv
  - pip inatall mysql-connector-python
  - pip inatall openpyxl

# Settings in Revit
For filtering elements parameter "BOQ Phase" is used.
All elements, that will be in BOQ have to have "BOQ Phase" parameter
to be filled usually with Design Change Number or Revision number.

The Revision info must be accurately filled in, as the
"name," "number", and "issued by" parameters are utilized as information
to be set up in the first list of Excel.

Ensure that the built-in parameters in the Revit family type are filled in correctly:
"Description" should contain a human-readable catalogue name for the element.
"Manufacturer" should provide a link to the product standard or information about
the manufacturer, along with the order number.

# Excel template
BOQ Excel file is created based on `boq_template.xlsx` that located in script folder.

**WARNING**
User not allowed to modify the template file. The code rigidly specifies the cell numbers for recording information in the table.The text formatting and font styles are pre-set in the Excel table template, impacting the visual appearance. Altering them may result in unpredictable consequences.

# Data base access
Access to database is provided with `db_info.env` file.
Please contact local admins to get the file.

# Run script in Dynamo

## Set Excel Path

## Set BOQ name and parameters manually

## Set BOQ name by info from SQL database
