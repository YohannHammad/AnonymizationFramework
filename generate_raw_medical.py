from anonymization.preprocessing import *
import faker
from random import choice

struct = {"id":DBTYPES.INTEGER(autoincrement=True, pk=True),
          "nom":DBTYPES.TEXT(),
          "prenom":DBTYPES.TEXT(),
          "sexe": DBTYPES.TEXT(),
          "date_naissance": DBTYPES.DATETIME(),
          "ville_lon": DBTYPES.REAL(),
          "ville_lat": DBTYPES.REAL(),
          "num_secu": DBTYPES.TEXT(),
          "groupe_sanguin": DBTYPES.TEXT(),
          "pathologie": DBTYPES.TEXT(),
          "severitee": DBTYPES.TEXT()
        }

db = Database("medical","localhost", "groupe_1_GDA", "")
db.dropTable("raw_pathologies_patients")
db.createTable("raw_pathologies_patients")
for col, type in struct.items():
    db.addColumn("raw_pathologies_patients", col, type)
db.commit()


def pathologies_patients_data_gen():
    line = {}
    f = faker.Faker()
    with open("cache/maladie_liste.txt", "r") as file:
        maladies = file.readlines()
    maladies = [elem.replace("\n","") for elem in maladies]
    while True:
        identity = f.profile()
        location = f.location_on_land()
        line["nom"] = f.first_name()
        line["prenom"] = f.last_name()
        line["sexe"] = identity["sex"]
        line["date_naissance"] = identity["birthdate"]
        line["ville_lat"] = location[0]
        line["ville_lon"] = location[1]
        line["num_secu"] = identity["ssn"]
        line["pathologie"] = choice(maladies)
        line["groupe_sanguin"] = identity["blood_group"]
        line["severitee"] = choice(["annodin", "preocupant", "severe", "letale"])
        yield line


db.generateMockData("raw_pathologies_patients", pathologies_patients_data_gen(), 100000)


