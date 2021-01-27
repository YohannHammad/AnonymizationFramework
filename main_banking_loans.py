from anonymization.annonymizeGDATable import *
from anonymization.preprocessing import *
import datetime

table_structure = {"loan_id":DBTYPES.INTEGER(),
                  "account_id":DBTYPES.INTEGER(),
                  "loan_date":DBTYPES.TEXT(),
                  "amount" : DBTYPES.INTEGER(),
                  "duration" : DBTYPES.INTEGER(),
                  "payments": DBTYPES.REAL(),
                  "status" : DBTYPES.TEXT(),
                  "acct_district_id" : DBTYPES.INTEGER(),
                  "frequency": DBTYPES.TEXT(),
                  "acct_date": DBTYPES.TEXT(),
                  "uid": DBTYPES.INTEGER(),
                  "disp_type": DBTYPES.TEXT(),
                  "birth_number" : DBTYPES.TEXT(),
                  "cli_district_id": DBTYPES.INTEGER(),
                  "lastname" : DBTYPES.TEXT(),
                  "firstname" : DBTYPES.TEXT(),
                  "birthdate" : DBTYPES.INTEGER(),
                  "gender" : DBTYPES.TEXT(),
                  "ssn" : DBTYPES.TEXT(),
                  "email" : DBTYPES.TEXT(),
                  "street" : DBTYPES.TEXT(),
                  "zip" : DBTYPES.TEXT()}

ignore_fields = ["loan_id", "account_id", "loan_date", "amount", "duration","payments", "status", "frequency", "acct_date", "uid", "birth_number",
                 "lastname", "firstname","ssn", "email", "zip"]
quid_cols = ["cli_district_id", "street", "birthdate", "acct_district_id"]
sensitive_cols = ["disp_type", "gender"]

position_fields = ["street"]
indexation = []

def birthDateToAge(ligne):
    currentyear = datetime.datetime.now().year
    return currentyear - datetime.datetime.strptime(ligne["birthdate"], "%Y-%m-%d").year

raw_transform = {"birthdate" : birthDateToAge}


annonymizeGDATable("groupe_1_GDA", "",                      #The credentials for the local database
                   "banking", "loans",                          #Database and table name for the local database
                   "raw_banking", "loans",                      #Database and table name for the GDA database
                   table_structure, ignore_fields, position_fields, indexation, quid_cols, sensitive_cols,
                   4,                                           #Value for K
                   2,
                   gda_raw_transform=raw_transform, use_cache=False)