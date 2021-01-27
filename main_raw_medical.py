from anonymization.annonymizeGDATable import *
from anonymization.preprocessing import *
import datetime


table_structure = {"nom":DBTYPES.TEXT(),
          "prenom":DBTYPES.TEXT(),
          "sexe": DBTYPES.TEXT(),
          "date_naissance": DBTYPES.DATETIME(),
          "ville_lat": DBTYPES.REAL(),
          "ville_lon": DBTYPES.REAL(),
          "num_secu": DBTYPES.TEXT(),
          "groupe_sanguin": DBTYPES.TEXT(),
          "pathologie": DBTYPES.TEXT(),
          "severitee": DBTYPES.TEXT()
        }

ignore_fields = ["nom", "prenom", "num_secu"]
position_fields = []
position_in_lat_lon = [("ville_lat", "ville_lon")]
indexation = ["sexe", "severitee", "groupe_sanguin"]
quid_cols = ["sexe", "ville_lat", "ville_lon", "date_naissance"]
sensitive_cols = ["groupe_sanguin", "pathologie", "severitee"]


# def birthDateToAge(ligne):
#     currentyear = datetime.datetime.now().year
#     return currentyear - datetime.datetime.strptime(ligne["birthdate"], "%Y-%m-%d").year

raw_transform = {}


annonymizeGDATable("groupe_1_GDA", "",
                   "medical", "pathologies_patients", "medical", "raw_pathologies_patients",
                   table_structure, ignore_fields, position_fields, indexation, quid_cols, sensitive_cols, 4, 2,
                   gda_raw_transform=raw_transform, postion_in_lat_lon=position_in_lat_lon, use_cache=False, local_table_already_created=True, str_sort_function=sortStringListBySimilarityButFast)

