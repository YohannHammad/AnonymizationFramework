from anonymization.annonymizeGDATable import *
from anonymization.preprocessing import *
import datetime


table_structure = {"datetime" : DBTYPES.DATETIME(),#
                    "doc": DBTYPES.TEXT(),         #
                    "uid": DBTYPES.TEXT(),         #
                    "country": DBTYPES.TEXT(),
                    "city": DBTYPES.TEXT(),
                    "lat": DBTYPES.TEXT(),
                    "long": DBTYPES.TEXT(),
                    "lastname": DBTYPES.TEXT(),    #
                    "firstname": DBTYPES.TEXT(),   #
                    "birthdate": DBTYPES.DATE(),   #
                    "gender": DBTYPES.TEXT(),
                    "ssn": DBTYPES.TEXT(),
                    "email": DBTYPES.TEXT(),
                    "street": DBTYPES.TEXT(),
                    "zip": DBTYPES.TEXT()}

ignore_fields = ["uid", "firstname", "lastname", "ssn", "email"]
position_fields = []
position_in_lat_lon = [("lat", "long")]
indexation = ["gender"]
quid_cols = []
sensitive_cols = ["datetime", "doc"]


# def birthDateToAge(ligne):
#     currentyear = datetime.datetime.now().year
#     return currentyear - datetime.datetime.strptime(ligne["birthdate"], "%Y-%m-%d").year

raw_transform = {}


annonymizeGDATable("groupe_1_GDA", "",
                   "scihub", "downloads", "raw_scihub", "downloads",
                   table_structure, ignore_fields, position_fields, indexation, quid_cols, sensitive_cols, 2, 1,
                   gda_raw_transform=raw_transform, postion_in_lat_lon=position_in_lat_lon)


