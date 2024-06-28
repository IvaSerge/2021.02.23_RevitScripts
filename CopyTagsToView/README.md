

<<details open>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-script">About the Script</a>
    </li>
    <li>
      <a href="#how-to-use-the-script">How to Use the Script</a>
      <ul>
        <li><a href="#script-parameters">Script Parameters</a></li>
      </ul>
    </li>
    <li><a href="#script">Script</a></li>
    <li><a href="#additional-notes">Additional Notes</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>!-- TABLE OF CONTENTS -->

# About the script
The script performs the following tasks:
1. Retrieves tag properties from the selected tags in the active view.
2. Copies the tags to a specified target view.
3. Updates the tag properties to match the original tags, including leader positions if applicable.

# How to Use the Script

1. **Select Tags**: Select the tags in the active Revit view that you want to copy.
2. **Switch to Target View**: In Revit change view to target view.
2. **Run the Script**: Run script in Dynamo.

### Script Parameters

- `IN[0]`: Directory path (not used directly in the script).
- `IN[1]`: Reload variable (not used directly in the script).
- `IN[2]`: Input elements (tags to be copied). If this is empty, the script will use the current selection.
