

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
Script creates Bill of Quantities (BOQ) as Excel and PDF.
File names are created automatically using Naming convention of the company.
No additional works with manual export of Revit schedules needed.

Script fills first page according to current Revit revision.  
Second page is the list of pages, effected by the change.  
Third page is the list of materials, including specific materials, that can't be calculated inside the Revit. As example - IT RJ45 Jacks and Patch cords.

**WARNING**
Still very specific families, like "busbars" of families, that are not from company standard BIM catalogue, may not be calculated correctly

# Installation of Python modules
Before script run be sure that all necessary Python modules were installed.

## **pip** installation
To install modules in Dynamo Python please check this link:
[pip install guide](https://github.com/DynamoDS/Dynamo/wiki/Customizing-Dynamo's-Python-3-installation)

**NOTE**
Revit 2023 use Python v.3.9.12  
While installation next Python path must be used:  
**%LocalAppData%\python-3.9.12-embed-amd64**

## Installation of python modules
  - pandas
  - Pillow
  - pypiwin32
  - python-dotenv
  - mysql-connector-python
  - openpyxl

# Settings in Revit

# Excel template

# Run script in Dynamo

## Set BOQ name and parameters manually

## Set BOQ name by info from SQL database
