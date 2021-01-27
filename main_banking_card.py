from anonymization.annonymizeGDATable import *
from anonymization.preprocessing import *
import datetime

table_structure = {"card_id": DBTYPES.INTEGER(),
                   "disp_id": DBTYPES.INTEGER(),
                   "card_type": DBTYPES.TEXT(),
                   "uid": DBTYPES.INTEGER(),
                   "disp_type": DBTYPES.TEXT(),
                   "birth_number": DBTYPES.INTEGER(),
                   "cli_district_id": DBTYPES.INTEGER(),
                   "lastname": DBTYPES.TEXT(),
                   "firstname": DBTYPES.TEXT(),
                   "birthdate": DBTYPES.INTEGER(),
                   "gender": DBTYPES.TEXT(),
                   "ssn": DBTYPES.TEXT(),
                   "email": DBTYPES.TEXT(),
                   "street": DBTYPES.TEXT(),
                   "zip": DBTYPES.TEXT()}

ignore_fields = ["ssn", "uid", "zip", "card_id", "disp_id", "disp_type", "birth_number", "lastname", "firstname",
                 "email", "issues"]
position_fields = ["street"]
indexation = []
quid_cols = ["cli_district_id", "street", "birthdate"]
sensitive_cols = ["card_type", "gender"]


def birthDateToAge(ligne):
    currentyear = datetime.datetime.now().year
    return currentyear - datetime.datetime.strptime(ligne["birthdate"], "%Y-%m-%d").year


raw_transform = {"birthdate": birthDateToAge}

annonymizeGDATable("groupe_1_GDA", "",
                   "banking", "cards", "raw_banking", "cards",table_structure, ignore_fields, position_fields,
                   indexation, quid_cols, sensitive_cols,4 , 2,
                   gda_raw_transform=raw_transform, use_cache=False)
