import clr
import os
import sys
import re

local_data = os.getenv("LOCALAPPDATA")
py_path = local_data + r"\python-3.9.12-embed-amd64\Lib\site-packages"
sys.path.append(py_path)

from dotenv import load_dotenv
import mysql.connector as connection
import pandas as pd

def check_file_name(file_name):

	# check for forbiden symbols
	for char in file_name:
		if char in "<:\"/\\|?*":
			raise ValueError("Wrong file name")

	# check file length	
	if len(file_name) > 230:
		raise ValueError("File name is too long")

	return True

def get_db_table(env_path, doc_name):
	env_name = "db_info.env"
	env_path = env_path + "\\" + env_name

	# get database environement
	load_dotenv(env_path)
	DB_HOST = os.getenv("DB_HOST")
	DB_NAME = os.getenv("DB_NAME")
	DB_PORT = os.getenv("DB_PORT")
	DB_PASS = os.getenv("DB_PASS")
	DB_USER = os.getenv("DB_USER")

	# open db and read info to dataframe
	mydb = None
	try:
		mydb = connection.connect(
			host=DB_HOST,
			port=DB_PORT,
			database=DB_NAME,
			user=DB_USER,
			passwd=DB_PASS,
			use_pure=True)

		query = "SELECT document_id, document_number, revision, title "
		query += "FROM  aconex.document_history "
		query += f"WHERE document_number = '{doc_name}'"

		df = pd.read_sql(query, mydb)
		idx = df.groupby("document_number")['document_id'].idxmax()
		values_by_max_id = df.loc[idx].values.tolist()

		mydb.close()
		return values_by_max_id[0][1:]

	except Exception as e:
		print(str(e))
		# raise ValueError(str(e))
		return None

	finally:
		try:
			mydb.close()
		except:
			pass


# def get_info_by_name(dir_path, boq_name, rev_doc_number, boq_descr):

# 	# read database and get table by boq name
# 	db_table = get_db_table(dir_path, boq_name)

# 	if db_table:
# 		# if info from the database was found
# 		# check revision
# 		db_rev = int(db_table[1])
# 		if int(rev_doc_number) <= db_rev:
# 			err_string = f"Revision number [{rev_doc_number:02d}] is too small\n"
# 			err_string += f"Use revision bigger then [{db_rev:02d}]"
# 			raise ValueError(err_string)
# 		boq_descr = db_table[2]


def get_db_boq_name_and_rev(env_path, shop_code, discipline_code):

	env_name = "db_info.env"
	env_path = env_path + "\\" + env_name

	# get database environement
	load_dotenv(env_path)
	DB_HOST = os.getenv("DB_HOST")
	DB_NAME = os.getenv("DB_NAME")
	DB_PORT = os.getenv("DB_PORT")
	DB_PASS = os.getenv("DB_PASS")
	DB_USER = os.getenv("DB_USER")

	# open db and read info to dataframe
	mydb = None
	try:
		mydb = connection.connect(
			host=DB_HOST,
			port=DB_PORT,
			database=DB_NAME,
			user=DB_USER,
			passwd=DB_PASS,
			use_pure=True)

		query = "SELECT document_id, document_number, filename, revision, discipline "
		query += "FROM aconex.document_history "
		query += f"WHERE filename like '%{shop_code}-00-LI-{discipline_code}-TSLA%' "
		query += "AND filetype = 'xls'"
		

		df = pd.read_sql(query, mydb)
		df_values = df.values.tolist()

		# nothing in DB
		if not df_values:
			boq_name = f"{shop_code}-00-LI-{discipline_code}-TSLA-00001"
			boq_revision_number = int(0)
			return boq_name, boq_revision_number

		# find max number
		regexp = re.compile(r"^.*-TSLA-(\d*)_")  # or take firs two symbols
		xls_names = [i[1] for i in df_values]
		get_number = lambda x: int(regexp.match(x).group(1))
		xls_numbers = [get_number(i) for i in xls_names]
		current_max_num = max(xls_numbers)

		# update number for next document
		next_num = current_max_num + 1
		boq_name = f"{shop_code}-00-LI-{discipline_code}-TSLA-{next_num:05d}"
		boq_revision_number = int(0)
		return boq_name, boq_revision_number

	except Exception as e:
		print(str(e))
		raise ValueError(str(e))
		# return None

	finally:
		try:
			mydb.close()
		except:
			pass
