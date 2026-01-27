import clr
import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

dir_path = IN[0].DirectoryName  # type: ignore
sys.path.append(dir_path)

# ================ Python imports
import re
import os

# ================ GLOBAL VARIABLES
reload_var = IN[1]  # type: ignore
obsidian_files_path = IN[2]  # type: ignore

def files_finder(obsidian_files_path):
	"""
	Find all *.md files in the folder including all subfolders.
	"""
	md_files = []
	for root, dirs, files in os.walk(obsidian_files_path):
		for file in files:
			if file.endswith('.md'):
				md_files.append(os.path.join(root, file))
	return md_files

def tag_renamer(file_path, tag_name, new_tag):
	"""
	Using regex to replace occurrences of tag_name with new_tag in the file content.
	Assumes tag_name is like '#CP' and new_tag is like '#Area/CP'.
	Handles hierarchical tags like '#CP/sub' -> '#Area/CP/sub' by capturing the subpath.
	Tags are assumed to be whole words, separated by spaces, punctuation, or end of line.
	"""
	# Define the regex pattern: match #CP optionally followed by /subpath (no spaces or other #)
	# Escape the prefix after # for safety, but in this case it's simple.
	prefix = tag_name[1:]  # e.g., 'CP'
	pattern = r'#' + re.escape(prefix) + r'(/[^#\s,]*)?'
	
	# Replacement: #Area/CP followed by the captured subpath
	new_prefix = new_tag[1:]  # e.g., 'Area/CP'
	replacement = r'#' + new_prefix + r'\1'
	
	try:
		with open(file_path, 'r', encoding='utf-8') as f:
			content = f.read()
		
		new_content = re.sub(pattern, replacement, content)
		
		# Only write if there was a change
		if new_content != content:
			with open(file_path, 'w', encoding='utf-8') as f:
				f.write(new_content)
			print(f"Updated tags in: {file_path}")
		else:
			print(f"No changes needed in: {file_path}")
			
	except Exception as e:
		print(f"Error processing {file_path}: {str(e)}")

def tags_to_properties(file_path):
	standard_properties_list = list()
	standard_properties_list.append("---")
	standard_properties_list.append("Area:")
	standard_properties_list.append("  - BR")
	standard_properties_list.append("  - CP")
	standard_properties_list.append("  - CPT")
	standard_properties_list.append("  - DU")
	standard_properties_list.append("  - PTP")
	standard_properties_list.append("  - TB2")
	standard_properties_list.append("  - Tilburg")
	standard_properties_list.append("DesignedBy:")
	standard_properties_list.append("  - MaksN")
	standard_properties_list.append("  - MeetG")
	standard_properties_list.append("  - RomanIsc")
	standard_properties_list.append("  - SI")
	standard_properties_list.append("  - VolodymirS")
	standard_properties_list.append("Status:")
	standard_properties_list.append("  - Checking")
	standard_properties_list.append("  - CostEstimate")
	standard_properties_list.append("  - Done")
	standard_properties_list.append("  - Pending")
	standard_properties_list.append("  - WorkInProgress")
	standard_properties_list.append("StartDate:")
	standard_properties_list.append("Responsible:")
	standard_properties_list.append("tags:")
	standard_properties_list.append("---")
	
	keep_always_list = list()
	keep_always_list.append("---")
	keep_always_list.append("Area:")
	keep_always_list.append("DesignedBy:")
	keep_always_list.append("Status:")
	keep_always_list.append("StartDate:")
	keep_always_list.append("Responsible:")
	keep_always_list.append("tags:")

	found_in_tags = sub_tags_in_file(file_path)
	
	# Fixed: extend returns None; instead, combine and use conditional logic for matching
	file_properties = []
	for prop in standard_properties_list:
		stripped = prop.strip()
		if stripped in keep_always_list or stripped == "---":
			file_properties.append(prop)
		elif prop.startswith("  - "):
			value = prop[4:].strip()
			if value in found_in_tags:
				file_properties.append(prop)
	
	# Insert/update frontmatter in the file
	try:
		with open(file_path, 'r', encoding='utf-8') as f:
			content = f.read()
		
		# Check if frontmatter exists (starts with ---)
		if content.strip().startswith('---'):
			# Find the end of existing frontmatter
			lines = content.splitlines()
			frontmatter_end = 0
			in_frontmatter = False
			for i, line in enumerate(lines):
				if line.strip() == '---':
					if not in_frontmatter:
						in_frontmatter = True
					else:
						frontmatter_end = i + 1
						break
			# Replace frontmatter with new one
			new_front = '\n'.join(file_properties) + '\n'
			new_content = new_front + '\n'.join(lines[frontmatter_end:]) if frontmatter_end > 0 else new_front + '\n' + content
		else:
			# Prepend new frontmatter
			new_front = '\n'.join(file_properties) + '\n\n'
			new_content = new_front + content
		
		# Only write if there was a change
		if new_content != content:
			with open(file_path, 'w', encoding='utf-8') as f:
				f.write(new_content)
			print(f"Updated properties in: {file_path}")
		else:
			print(f"No changes needed in: {file_path}")
			
	except Exception as e:
		print(f"Error processing {file_path}: {str(e)}")

def sub_tags_in_file(file_path):
	tags_list = []
	try:
		with open(file_path, 'r', encoding='utf-8') as f:
			content = f.read()
		# With re find all tags pattern is r"#\w*\/(\w*)"
		# Return all group1 that found (unique subs)
		pattern = r"#\w*\/(\w*)"
		matches = re.findall(pattern, content)
		tags_list = list(set(matches))  # Unique sub-tags
	except Exception as e:
		print(f"Error reading {file_path}: {str(e)}")
	return tags_list

def clean_all_properties(file_path):
	"""
	Remove the entire YAML frontmatter block if the file starts with '---'.
	Removes all lines from the first '---' up to and including the second '---'.
	Additionally, removes any leading empty lines immediately after the frontmatter removal.
	Preserves the rest of the file content.
	"""
	try:
		with open(file_path, 'r', encoding='utf-8') as f:
			content = f.read()
		
		lines = content.splitlines(keepends=True)  # Preserve line endings
		
		if not lines or not lines[0].strip().startswith('---'):
			print(f"No frontmatter found in: {file_path} (does not start with '---')")
			return  # No change needed
		
		# Find the end of the frontmatter (second '---')
		frontmatter_end = -1
		in_frontmatter = True  # Assume starts in frontmatter
		for i, line in enumerate(lines):
			if i == 0:
				continue
			if line.strip() == '---':
				if in_frontmatter:
					# First '---' already passed; this is the second
					frontmatter_end = i + 1
					break
				else:
					# Reset if somehow out, but shouldn't happen
					in_frontmatter = True
			elif line.strip():  # Non-empty line after first '---'
				in_frontmatter = True  # Still in frontmatter until second '---'
		
		if frontmatter_end == -1:
			print(f"Malformed frontmatter (no closing '---') in: {file_path}. Skipping removal.")
			return  # No complete frontmatter to remove
		
		# Slice the content after the frontmatter
		remaining_lines = lines[frontmatter_end:]
		
		# Remove leading empty lines from the remaining content
		non_empty_start = 0
		for i, line in enumerate(remaining_lines):
			if line.strip():  # First non-empty line
				non_empty_start = i
				break
		cleaned_remaining = ''.join(remaining_lines[non_empty_start:])
		
		# Only write if there was a change (i.e., frontmatter was present and removed)
		if cleaned_remaining != content:
			with open(file_path, 'w', encoding='utf-8') as f:
				f.write(cleaned_remaining)
			print(f"Removed frontmatter and leading empty lines from: {file_path}")
		else:
			print(f"No changes needed in: {file_path}")
			
	except Exception as e:
		print(f"Error processing {file_path}: {str(e)}")

# ================ Main Logic
tag_name = "#VolodymirS"
new_tag = "#DesignedBy/VolodymirS"
all_files_in_folder = files_finder(obsidian_files_path)

for md_file in all_files_in_folder:
	# tag_renamer(md_file, tag_name, new_tag)
	# tags_to_properties(md_file)
	clean_all_properties(md_file)

OUT = obsidian_files_path
