# ================ Python imports
import math


cab_lst = list()

# cross-section | R Om/km | X Om/km
cab_lst.append(["1-#1.5, 1-#1.5, 1-#1.5", 13.384, 0.08])
cab_lst.append(["1-#1.5, 1-#1.5 mm, 1-#1.5", 13.384, 0.08])
cab_lst.append(["1-#2.5, 1-#2.5 mm, 1-#2.5", 8.855, 0.08])
cab_lst.append(["1-#4, 1-#4 mm, 1-#4", 5.509, 0.08])
cab_lst.append(["1-#6, 1-#6 mm, 1-#6", 3.681, 0.08])
cab_lst.append(["1-#10, 1-#10 mm, 1-#10", 2.187, 0.08])
cab_lst.append(["1-#16, 1-#16 mm, 1-#16", 1.374, 0.08])
cab_lst.append(["3-#1.5, 1-#1.5, 1-#1.5", 13.384, 0.08])
cab_lst.append(["3-#2.5, 1-#2.5", 8.855, 0.08])
cab_lst.append(["3-#2.5, 1-#2.5 mm, 1-#2.5", 8.855, 0.08])
cab_lst.append(["3-#4, 1-#4", 5.509, 0.08])
cab_lst.append(["3-#4, 1-#4 mm, 1-#4", 5.509, 0.08])
cab_lst.append(["3-#6, 1-#6", 3.681, 0.08])
cab_lst.append(["3-#6, 1-#6 mm, 1-#6", 3.681, 0.08])
cab_lst.append(["3-#10, 1-#10", 2.187, 0.08])
cab_lst.append(["3-#10, 1-#10 mm, 1-#10", 2.187, 0.08])
cab_lst.append(["3-#16, 1-#16", 1.374, 0.08])
cab_lst.append(["3-#16, 1-#16 mm, 1-#16", 1.374, 0.08])
cab_lst.append(["3-#25, 1-#16", 0.869, 0.08])
cab_lst.append(["3-#25, 1-#25 mm, 1-#16", 0.869, 0.08])
cab_lst.append(["3-#35, 1-#16", 0.626, 0.08])
cab_lst.append(["3-#35, 1-#35 mm, 1-#16", 0.626, 0.08])
cab_lst.append(["3-#50, 1-#25", 0.462, 0.08])
cab_lst.append(["3-#50, 1-#50 mm, 1-#25", 0.462, 0.08])

cab_lst.append(["3-#70, 1-#35", 0.320, 0.08])
cab_lst.append(["3-#70, 1-#70 mm, 1-#35", 0.320, 0.08])
cab_lst.append(["2 runs of 3-#70, 1-#70", 0.16, 0.04])
cab_lst.append(["2 runs of 3-#70, 1-#70 mm, 1-#70 mm", 0.16, 0.04])

cab_lst.append(["3-#95, 1-#50", 0.231, 0.08])
cab_lst.append(["3-#95, 1-#95 mm, 1-#50", 0.231, 0.08])

cab_lst.append(["3-#120, 1-#70", 0.183, 0.08])
cab_lst.append(["2 runs of 3-#120, 1-#70", 0.0915, 0.04])
cab_lst.append(["3 runs of 3-#120, 1-#70", 0.061, 0.027])
cab_lst.append(["4 runs of 3-#120, 1-#70", 0.0458, 0.02])

cab_lst.append(["3-#120, 1-#120 mm, 1-#70", 0.183, 0.08])
cab_lst.append(["2 runs of 3-#120, 1-#120 mm, 1-#70", 0.0915, 0.04])
cab_lst.append(["3 runs of 3-#120, 1-#120 mm, 1-#70", 0.061, 0.027])
cab_lst.append(["4 runs of 3-#120, 1-#120 mm, 1-#70", 0.0458, 0.02])
cab_lst.append(["5 runs of 3-#120, 1-#120 mm, 1-#70", 0.0366, 0.016])
cab_lst.append(["6 runs of 3-#120, 1-#120 mm, 1-#70", 0.0305, 0.014])

cab_lst.append(["3-#150, 1-#70", 0.148, 0.08])
cab_lst.append(["2 runs of 3-#150, 1-#70", 0.074, 0.04])
cab_lst.append(["3 runs of 3-#150, 1-#70", 0.049, 0.027])
cab_lst.append(["4 runs of 3-#150, 1-#70", 0.037, 0.02])
cab_lst.append(["5 runs of 3-#150, 1-#70", 0.0296, 0.016])
cab_lst.append(["6 runs of 3-#150, 1-#70", 0.0247, 0.014])

cab_lst.append(["3-#150, 1-#150 mm, 1-#70", 0.148, 0.027])
cab_lst.append(["2 runs of 3-#150, 1-#150 mm, 1-#70", 0.074, 0.04])
cab_lst.append(["4 runs of 3-#150, 1-#150 mm, 1-#70", 0.037, 0.02])
cab_lst.append(["5 runs of 3-#150, 1-#150 mm, 1-#70", 0.0296, 0.016])
cab_lst.append(["6 runs of 3-#150, 1-#150 mm, 1-#70", 0.0247, 0.014])
cab_lst.append(["7 runs of 3-#150, 1-#150 mm, 1-#70", 0.0211, 0.011])
cab_lst.append(["8 runs of 3-#150, 1-#150 mm, 1-#70", 0.0185, 0.01])

cab_lst.append(["3-#160, 1-#160, 1-#160", 0.042, 0.013])  # Siemens busbar 1600A


def get_cable(section):
	"""
	get cable by type and cross-section

	args:
		section (str): cross-section of cable`
	"""
	# parameter is empty
	if not section:
		return None

	global cab_lst
	try:
		cable = [x for x in cab_lst if section in x[0]][0]
		return cable
	except:
		# cable not found
		return 0
		# raise ValueError(
		# 	"Cable not in catalogue \n %s" % section)
