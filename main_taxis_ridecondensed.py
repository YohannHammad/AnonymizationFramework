from anonymization.annonymizeGDATable import *
from anonymization.preprocessing import *
import datetime


table_structure = {"pickup_datetime":DBTYPES.DATETIME(),
                   "dropoff_datetime": DBTYPES.DATETIME(),
                   "pickup_latitude": DBTYPES.REAL(),
                   "pickup_longitude": DBTYPES.REAL(),
                   "dropoff_latitude": DBTYPES.REAL(),
                   "dropoff_longitude": DBTYPES.REAL()}

ignore_fields = []
position_fields = []
position_in_lat_lon = [("pickup_latitude", "pickup_longitude"), ("dropoff_latitude", "dropoff_longitude")]
indexation = []
quid_cols = ["pickup_latitude", "pickup_longitude", "dropoff_latitude", "dropoff_longitude"]
sensitive_cols = ["pickup_datetime", "dropoff_datetime"]


# def birthDateToAge(ligne):
#     currentyear = datetime.datetime.now().year
#     return currentyear - datetime.datetime.strptime(ligne["birthdate"], "%Y-%m-%d").year

raw_transform = {}


annonymizeGDATable("groupe_1_GDA", "",
                   "taxis", "rides_condensed", "raw_taxi", "rides_condensed",
                   table_structure, ignore_fields, position_fields, indexation, quid_cols, sensitive_cols, 2, 1,
                   gda_raw_transform=raw_transform, postion_in_lat_lon=position_in_lat_lon)

