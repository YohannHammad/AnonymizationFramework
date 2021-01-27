from anonymization.annonymizeGDATable import *
from anonymization.preprocessing import *
import datetime
from anonymization.annonymizeGDATable import *
import threading

convert_synthax = [
    ["TEXT", DBTYPES.TEXT()],
    ["INTEGER", DBTYPES.INTEGER()],
    ["DATETIME", DBTYPES.DATETIME()],
    ["DATE", DBTYPES.DATE()],
    ["REAL", DBTYPES.REAL()]
]
ignore_fields = []
position_fields = []
indexation = []
quid_cols = []
sensitive_fields = []

tab_informations = {}


def getDatas(tab):
    global tab_informations
    tab_informations = tab


def processData(dict_data, tab_option):
    table_structure = {}

    for key, values in dict_data.items():
        for tuple in convert_synthax:
            if values[0] == tuple[0]:
                table_structure[key] = tuple[1]

        # très moche mais fonctionnel
        if len(values) > 1:
            for val in values[1:]:
                if val == 'ignore_field':
                    ignore_fields.append(key)
                if val == 'position_fields':
                    position_fields.append(key)
                if val == 'indexation':
                    indexation.append(key)
                if val == 'quid_cols':
                    quid_cols.append(key)
                if val == 'sensitive_fields':
                    sensitive_fields.append(key)

    bd_source = tab_informations["BD_source"]
    tab_source = tab_informations["Table_source"]
    bd_dest = tab_informations["BD_dest"]
    tab_dest = tab_informations["Table_dest"]
    k_value = tab_informations["k_value"]
    l_value = tab_informations["l_value"]

    def birthDateToAge(ligne):
        currentyear = datetime.datetime.now().year
        return currentyear - datetime.datetime.strptime(ligne["birthdate"], "%Y-%m-%d").year

    raw_transform = {"birthdate": birthDateToAge}

    print(position_fields)

    thread = threading.Thread(
        target=lambda: annonymizeGDATable("groupe_1_GDA", "", bd_dest, tab_dest, bd_source, tab_source,
                                          table_structure, ignore_fields, position_fields, indexation, quid_cols,
                                          sensitive_fields, k_value, l_value,
                                          gda_raw_transform=raw_transform, use_cache=False))
    thread.start()