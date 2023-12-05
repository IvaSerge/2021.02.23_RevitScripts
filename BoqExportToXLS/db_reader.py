import clr
import os
import sys


local_data = os.getenv("LOCALAPPDATA")
py_path = local_data + r"\python-3.9.12-embed-amd64\Lib\site-packages"
sys.path.append(py_path)

from dotenv import load_dotenv
import mysql.connector as connection
import pandas as pd


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

		query = "SELECT id, document_number, revision, title "
		query += "FROM  aconex.document_history "
		query += f"WHERE document_number = '{doc_name}'"

		df = pd.read_sql(query, mydb)
		idx = df.groupby("document_number")['id'].idxmax()
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


def get_info_by_name(dir_path, boq_name, rev_doc_number, boq_descr):

	# read database and get table by boq name
	db_table = get_db_table(dir_path, boq_name)

	if db_table:
		# if info from the database was found
		# check revision
		db_rev = int(db_table[1])
		if int(rev_doc_number) <= db_rev:
			err_string = f"Revision number [{rev_doc_number}] is too small\n"
			err_string += f"Use revision bigger then [{db_rev}]"
			raise ValueError(err_string)
		boq_descr = db_table[2]

	name_number = boq_name
	name_prefix = "_XLSX"
	name_rev = f'[{rev_doc_number:02d}]'
	name_description = boq_descr

	name_xlsx = boq_name
	name_xlsx += name_prefix + name_rev
	name_xlsx += " - BOQ - " + name_description
	name_xlsx += ".xlsx"

	name_pdf = name_number
	name_pdf += name_rev
	name_pdf += " - BOQ - " + name_description
	name_pdf += ".pdf"

	return name_xlsx, name_pdf
