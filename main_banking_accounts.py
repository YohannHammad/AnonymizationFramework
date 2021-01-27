from anonymization.annonymizeGDATable import *
from anonymization.preprocessing import *
import datetime
table_structure = {"account_id":DBTYPES.INTEGER(),
                  "acct_district_id":DBTYPES.INTEGER(),
                  "frequency":DBTYPES.TEXT(),
                  "acct_date":DBTYPES.INTEGER(),
                  "uid" : DBTYPES.INTEGER(),
                  "disp_type" : DBTYPES.TEXT(),
                  "birth_number": DBTYPES.INTEGER(),
                  "cli_district_id" : DBTYPES.INTEGER(),
                  "lastname" : DBTYPES.TEXT(),
                  "firstname": DBTYPES.TEXT(),
                  "birthdate": DBTYPES.INTEGER(),
                  "gender": DBTYPES.TEXT(),
                  "ssn": DBTYPES.TEXT(),
                  "email" : DBTYPES.TEXT(),
                  "street": DBTYPES.TEXT(),
                  "zip" : DBTYPES.TEXT()}

ignore_fields = ["ssn", "uid", "zip", "card_id", "acct_district_id", "disp_type", "birth_number", "lastname", "firstname", "email"]
position_fields = ["street"]
indexation = []
quid_cols = ["cli_district_id", "street", "birthdate"]
sensitive_cols = ["frequency", "gender"]


def birthDateToAge(ligne):
    currentyear = datetime.datetime.now().year
    return currentyear - datetime.datetime.strptime(ligne["birthdate"], "%Y-%m-%d").year

raw_transform = {"birthdate" : birthDateToAge}


annonymizeGDATable("groupe_1_GDA", "", "banking", "accounts", "raw_banking", "accounts",
                   table_structure, ignore_fields, position_fields, indexation, quid_cols, sensitive_cols,4 , 2,
                   gda_raw_transform=raw_transform, use_cache=False)


