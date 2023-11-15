import clr
import os
import sys


local_data = os.getenv("LOCALAPPDATA")
py_path = local_data + r"\python-3.9.12-embed-amd64\Lib\site-packages"
sys.path.append(py_path)

from dotenv import load_dotenv
import mysql.connector as connection
import pandas as pd


def get_info_by_name(boq_name, path_dir):
	env_name = "db_info.env"
	env_path = path_dir + "\\" + env_name

	# get database environement
	load_dotenv(env_path)
	DB_HOST = os.getenv("DB_HOST")
	DB_NAME = os.getenv("DB_NAME")
	DB_PORT = os.getenv("DB_PORT")
	DB_PASS = os.getenv("DB_PASS")
	DB_USER = os.getenv("DB_USER")

	# open db and read info to dataframe
	try:
		mydb = connection.connect(
			host=DB_HOST,
			port=DB_PORT,
			database=DB_NAME,
			user=DB_USER,
			passwd=DB_PASS,
			use_pure=True)

		# query = "Select * from studentdetails;"
		query = "SELECT * FROM level_name"

		result_dataFrame = pd.read_sql(query, mydb)
		print(result_dataFrame)
		mydb.close()

	except Exception as e:
		mydb.close()
		print(str(e))
		raise ValueError(str(e))

	return DB_PASS
