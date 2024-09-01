# ================ Python imports
import math
import re

def get_cable(section_str):
	"""
	get cable by type and cross-section

	args:
		section (str): cross-section of cable`
	"""
	cab_dict = { 
		# cross-section | R Om/km | X Om/km
		"1.5": [13.384, 0.08],
		"2.5": [8.855, 0.08],
		"4": [5.509, 0.08],
		"6": [3.681, 0.08],
		"10": [2.187, 0.08],
		"16": [1.374, 0.08],
		"25": [0.869, 0.08],
		"35": [0.626, 0.08],
		"50": [0.462, 0.08],
		"70": [0.320, 0.08],
		"95": [0.231, 0.08],
		"120": [0.183, 0.08],
		"150": [0.148, 0.08],
		"160": [0.042, 0.013],
		"3200": [0.019, 0.005]
	}

	# parameter is empty
	if not section_str:
		return 0, 0

	regexp = re.compile(r"^(?:(\d*) runs of )?\d-#(\d*\.?\d),")
	check = regexp.match(section_str)

	if check:
		groups_found = len([group for group in check.groups()])

		# check number of runs
		if check.group(1):
			n_of_runs = int(check.group(1))
			# n_of_runs = check.group(1)
		else:
			n_of_runs = 1

		# get R and X if possible by cable size
		if check.group(2):
			cable_size = check.group(2)
			cable_R = cab_dict.get(cable_size)[0]
			cable_X = cab_dict.get(cable_size)[1]
			return cable_R / n_of_runs, cable_X / n_of_runs
		else:
			return 0, 0

	else:
		return 0, 0
