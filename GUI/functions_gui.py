import csv
import psycopg2
import os


def parametrageTable(tab_infos, limit=0):
    conn = psycopg2.connect(
        host="db001.gda-score.org",
        database=tab_infos["BD_source"],
        user="gda-score_ro_user",
        password="moquaiR7")

    cur = conn.cursor()
    tab_source_name = tab_infos["Table_source"]
    list_temp = []
    s = f"SELECT * FROM {tab_source_name} LIMIT {limit}"
    sql = "COPY ({0}) TO STDOUT WITH CSV HEADER".format(s)
    with open("test.csv", "w+") as out:
        att_csv = csv.reader(out)
        cur.copy_expert(sql, out)

def getAttributs():
    f = open("test.csv", "r")
    lines = f.read().split("\n")
    list_attributs = []

    for line in lines:
        if line != "":
            cols = line.split(",")
            list_attributs = cols

    f.close()
    os.remove("test.csv")
    return list_attributs

