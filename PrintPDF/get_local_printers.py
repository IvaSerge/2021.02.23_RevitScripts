
# LINK: https://www.youtube.com/watch?v=zZt2ctV5Mos

import subprocess
# data = subprocess.check_output(["wmic", "printer", "list", "brief"]).decode("utf-8").split("\r\r\n")
data = subprocess.check_output(["wmic", "printer", "list", "brief"]).decode("utf-8").split("\r\r\n")

printer_names = list()
for line in data:
	for printername in line.split("  "):
		if printername != "":
			printer_names.append(printername)
			break

OUT = printer_names[1:]
