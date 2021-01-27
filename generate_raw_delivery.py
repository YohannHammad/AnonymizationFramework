from anonymization.preprocessing import *
import faker
from random import choice
import csv
import datetime
struct = {"id":DBTYPES.INTEGER(autoincrement=True, pk=True),
          "nom":DBTYPES.TEXT(),
          "prenom":DBTYPES.TEXT(),
          "addresse_livraison_lat": DBTYPES.REAL(),
          "addresse_livraison_lon": DBTYPES.REAL(),
          "mode_payement": DBTYPES.TEXT(),
          "mode_livraison": DBTYPES.TEXT(),
          "prix": DBTYPES.REAL(),
          "date_mise_en_vente": DBTYPES.DATE(),
          "date_achat": DBTYPES.DATE(),
          "type_produit": DBTYPES.TEXT(),
          "nom_produit": DBTYPES.TEXT(),
          "poid_produit": DBTYPES.TEXT()
        }

db = Database("delivery", "localhost", "groupe_1_GDA", "")
db.dropTable("raw_delivery")
db.createTable("raw_delivery")
for col, type in struct.items():
    db.addColumn("raw_delivery", col, type)
db.commit()


def pathologies_patients_data_gen():
    line = {}
    f = faker.Faker()
    products = []
    with open("cache/products.csv", "r") as file:
        reader = csv.DictReader(file)
        for p in reader: products.append(p)
    while True:
        location = f.location_on_land()
        product = choice(products)
        line["nom"] = f.first_name()
        line["prenom"] = f.last_name()
        line["addresse_livraison_lat"] = location[0]
        line["addresse_livraison_lon"] = location[1]
        line["mode_payement"] = choice(["CB", "Paypal", "Chèque", "Monnaie"])
        line["mode_livraison"] = choice(["Domicile", "Point Relais", "Retrait Magasin"])
        line["date_mise_en_vente"] = datetime.datetime.strptime(product["sellstartdate"], "%Y-%m-%d")
        line["date_achat"] = line["date_mise_en_vente"] + datetime.timedelta(days=random.randint(0,1000))
        line["prix"] = product["standardcost"]
        line["type_produit"] =product["productcategory.name"]
        line["nom_produit"] = product["product.name"]
        line["poid_produit"] = product["weight"]
        yield line
db.generateMockData("raw_delivery", pathologies_patients_data_gen(), 100000)


