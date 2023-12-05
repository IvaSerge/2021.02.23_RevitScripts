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


def get_boq_filename(env_path, shop_code, discipline_code):

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
		query += f"WHERE filename like '{shop_code}%TSLA-8000%' "
		query += f"AND discipline like '{discipline_code} -%' "
		query += "AND filetype = 'xls'"

		df = pd.read_sql(query, mydb)
		df_values = df.values.tolist()

		# nothing in DB
		if not df_values:
			boq_name = f"{shop_code}-00-SH-{discipline_code}-TSLA_8000-00"
			boq_revision_number = int(0)
			return boq_name, boq_revision_number

		current_max_name = df_values[-1][1]
		regexp = re.compile(r"^.*-8000-(\d*)_")  # or take firs two symbols
		check = regexp.match(current_max_name)
		current_max_num = int(check.group(1))
		next_num = current_max_num + 1
		boq_name = f"{shop_code}-00-SH-{discipline_code}-TSLA_8000-{next_num:02d}"
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
