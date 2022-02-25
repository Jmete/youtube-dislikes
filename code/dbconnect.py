# This file is intended to open a connection to the postgres database
# where we will be loading and retrieving our youtube data.

import psycopg2 as psy
import yaml

def get_connection():

    config = yaml.safe_load(open('././config.yml'))

    host = config["config"]["dbip"]
    database = config["config"]["dbname"]
    user = config["config"]["dbuser"]
    pw = config["config"]["dbpw"]

    try:
        conn = psy.connect(host=host,database=database,user=user,password=pw)
        return conn
    except:
        print("Cannot connect to the database")

