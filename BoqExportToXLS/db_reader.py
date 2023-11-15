import clr
import os
import sys


local_data = os.getenv("LOCALAPPDATA")

py_path = local_data + r"\python-3.9.12-embed-amd64\Lib\site-packages"
sys.path.append(py_path)

from dotenv import load_dotenv


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

	return DB_PASS
