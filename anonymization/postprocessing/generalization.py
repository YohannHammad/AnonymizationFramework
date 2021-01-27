import datetime
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="gda_generalization")
import csv
import sys
import pprint

class Generalization:
    def __init__(self, k, file_name, out_name, quids):
        """
        Instanciation of the database
        :param k: value of k-anonymity
        :param file_name: name of the file containing the non-generalised database
        :param out_name: name of the file containing the generalised database
        """
        print("Generalization's initialization")
        self.k = k;
        self.file_name = file_name
        self.out = out_name
        self.data_base = []
        self.quids = quids
        self.positions = [(quid_name, f"lon_{quid_name[4:]}") for quid_name in self.quids if quid_name[:4] == "lat_"]
        self.minmax = [colname for colname in self.quids]
        self.load()

    def load(self):
        """
        Loads the database in memory
        """
        tmp_data_base = []
        with open(self.file_name, newline='') as csvfile:
            spamreader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                del row["id"]
                tmp_data_base.append(row)

        i = 0
        j = 0
        while (i < len(tmp_data_base)):
            cluster = []
            while tmp_data_base[i][list(tmp_data_base[i].keys())[0]] != "NULL":
                cluster.append(tmp_data_base[i])
                i += 1
            i += 1
            self.data_base.append(cluster)
        print(len(self.data_base), "clusters generated, min cluster size", min([len(c) for c in self.data_base]),", max cluster size", max([len(c) for c in self.data_base]))


    def print_all(self):
        """
        Displays the database
        """
        i = 1
        for cluster in self.data_base:
            print("cluster {}:".format(i))
            for linea in cluster:
                print(linea)
            i += 1

    def generalize(self, dezoom_long_lat=False):
        """
        Generalises the database. Standardizes the quasi-identifiers of the lines of the same cluster.
        :param dezoom_long_late: boolean defining if the api is used to change the long/lat (more secure, but MUCH longer)
        """
        print("Generalization begins")
        i = 1

        for cluster in self.data_base:
            for linea in cluster:
                if dezoom_long_lat:
                    for lat_col,lon_col in self.positions:
                        try:
                            location = geolocator.reverse(str(linea[lat_col]) + "," + str(linea[lon_col]))
                            newAddress = []
                            if "township" in location.raw["address"]:
                                newAddress.append(location.raw["address"]["township"])
                            elif "village" in location.raw["address"]:
                                newAddress.append(location.raw["address"]["village"])
                            elif "hamlet" in location.raw["address"]:
                                newAddress.append(location.raw["address"]["hamlet"])
                            elif "city" in location.raw["address"]:
                                newAddress.append(location.raw["address"]["city"])
                            elif "municipality" in location.raw["address"]:
                                newAddress.append(location.raw["address"]["municipality"])
                            elif "town" in location.raw["address"]:
                                newAddress.append(location.raw["address"]["town"])
                            elif "county" in location.raw["address"]:
                                newAddress.append(location.raw["address"]["county"])
                            elif "state_district" in location.raw["address"]:
                                newAddress.append(location.raw["address"]["state_district"])
                            else:
                                print("Attention, city.\n{}".format(location.raw["address"]))
                            if "state" in location.raw["address"]:
                                newAddress.append(location.raw["address"]["state"])
                            elif "region" in location.raw["address"]:
                                newAddress.append(location.raw["address"]["region"])
                            elif "province" in location.raw["address"]:
                                newAddress.append(location.raw["address"]["province"])
                            elif "county" in location.raw["address"]:
                                newAddress.append(location.raw["address"]["county"])
                            else:
                                print("Attention, state/region.\n{}".format(location.raw["address"]))
                            if "country" in location.raw["address"]:
                                newAddress.append(location.raw["address"]["country"])
                            else:
                                print("ATTENTION, country.\n{}".format(location.raw["address"]))
                            genlocation = geolocator.geocode(",".join(newAddress))
                            linea[lat_col] = genlocation.latitude
                            linea[lon_col] = genlocation.longitude
                            # print("linea {}/{}...".format(i, ((len(self.data_base) - 1) * self.k)))
                        except:
                            print("CRITICAL ERROR, GPS coordinates were not found.")
                            #self.export(True)
                            sys.exit(0)
                i += 1
                # print(linea)
                # tmp2.append(float(linea[1]))
                # tmp3.append(float(linea[2]))
            min_clust = {}
            max_clust = {}
            for linea in cluster:
                for col in self.minmax:
                    mi = min(cluster, key=lambda line: line[col])[col]
                    ma = max(cluster, key=lambda line: line[col])[col]
                    if col not in min_clust: min_clust[col] = mi
                    if col not in max_clust: max_clust[col] = ma

                    if mi < min_clust[col]: min_clust[col] = mi
                    if ma > max_clust[col]: max_clust[col] = ma

            for linea in cluster:
                for col in max_clust:
                    linea[col] = f"[{min_clust[col]},{max_clust[col]}]"
        print("Generalization done")

    def export(self, error=False):
        """
        Exports the database in csv format
        :param error: boolean checking that the generalisation has gone well
        """
        with open(self.out, 'w', newline='') as csvfile:
            spamwriter = csv.DictWriter(csvfile, self.data_base[0][0].keys() , delimiter=',')
            spamwriter.writeheader()
            for cluster in self.data_base:
                for linea in cluster:
                    spamwriter.writerow(linea)
        print("Exportation successful")