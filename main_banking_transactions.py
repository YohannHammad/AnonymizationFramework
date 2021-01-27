from anonymization.annonymizeGDATable import *
from anonymization.preprocessing import *
import datetime

table_structure = {"trans_id":DBTYPES.INTEGER(),
                  "account_id":DBTYPES.INTEGER(),
                  "trans_date":DBTYPES.TEXT(),
                  "trans_type":DBTYPES.TEXT(),
                  "operation":DBTYPES.TEXT(),
                  "amount" : DBTYPES.REAL(),
                  "balance":DBTYPES.REAL(),
                  "k_symbol":DBTYPES.TEXT(),
                  "bank":DBTYPES.TEXT(),
                  "account":DBTYPES.TEXT(),
                  "acct_district_id" : DBTYPES.INTEGER(),
                  "frequency": DBTYPES.TEXT(),
                  "acct_date": DBTYPES.INTEGER(),
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
                  
ignore_fields = ["trans_id", "account_id", "trans_date", "trans_type", "operation", "amount", "balance", "k_symbol", "bank", "account", "duration", "frequency", 
                "payments", "status", "uid", "birth_number", "lastname", "firstname","ssn", "email", "zip", "acct_date"]
quid_cols = ["cli_district_id", "street", "birthdate", "acct_district_id"]
sensitive_cols = ["disp_type", "gender"]

position_fields = ["street"]
indexation = []

def birthDateToAge(ligne):
    currentyear = datetime.datetime.now().year
    return currentyear - datetime.datetime.strptime(ligne["birthdate"], "%Y-%m-%d").year

raw_transform = {"birthdate" : birthDateToAge}


annonymizeGDATable("groupe_1_GDA", "",                      #The credentials for the local database
                   "banking", "transactions",                          #Database and table name for the local database
                   "raw_banking", "transactions",                      #Database and table name for the GDA database
                   table_structure, ignore_fields, position_fields, indexation, quid_cols, sensitive_cols,
                   4,                                           #Value for K
                   1,
                   gda_raw_transform=raw_transform, use_cache=True, str_sort_function=sortStringListBySimilarityButVeryFast)