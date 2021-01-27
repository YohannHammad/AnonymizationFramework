# -*-coding: utf-8 -*-

import csv
import sys
import pprint
import numpy as np

class cluster_throw:
    def __init__(self):
        """
        a cluster that does not satisfy l-diversity
        """
        self.data = []
        self.numberOfSensitiveLDiverse = 0


class l_div_naive:
    def __init__(self, l, file_name, sensitive, quids, pk_colname):
        """
        l-diversite of the base
        :param l: value of l-diversity
        :param file_name: name of the file containing the non-generalised database
        :param sensitive: name of sensitive data columns
        :param quids: name of the quasi-identifier columns
        :param pk_name: name of the identifying columns
        """
        print("L-diversity naive will be initialized")
        self.l = l;
        self.file_name = file_name
        self.data_base = []
        self.sensitive = sensitive
        self.row = pk_colname+quids+sensitive
        self.load()
        print("L-diversity naive initialized")

    def load(self):
        """
        Loads the database in memory
        """
        tmp_data_base = []
        with open(self.file_name, newline='') as csvfile:
            spamreader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                #del row["id"]
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
        print(len(self.data_base),"clusters generated, min cluster size", min([len(c) for c in self.data_base]), ", max cluster size", max([len(c) for c in self.data_base]))

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

    def diversification(self, remisage):
        """
        Applies the l-diversity algorithm as long as all clusters are not l-diverse
        :param remisage: boolean that indicates if you mix clusters that do not satisfy the l-diversity
        """
        run = True
        i = 1
        while run:
            i+=1

            run = False
            
            self.process(remisage)

            for data_piece in self.sensitive:
                for cluster in self.data_base:
                    tmp=[]
                    for linea in cluster:
                        tmp.append(linea[f"{data_piece}"])
                    if len(np.unique(tmp)) < self.l:
                        run = True

                        

    def process(self, remisage):
        """
        Calculates whether the l-diversity is respected (for each sensitive data), and removes unsatisfactory clusters.
        :param remisage: boolean that indicates if you mix clusters that do not satisfy the l-diversity
        """
        data_base_throw = []
       
        for data_piece in self.sensitive:
            for cluster in self.data_base:
                tmp=[]
                for linea in cluster:
                    tmp.append(linea[f"{data_piece}"])
                if len(np.unique(tmp)) < self.l:
                    tmp_cluster = cluster_throw()
                    for linea in cluster:
                        tmp_cluster.data.append(linea)

                    data_base_throw.append(tmp_cluster)
                    self.data_base.remove(cluster)
                    
        if remisage:
            self.remisage(data_base_throw)


    def remisage(self, data_base_throw):
        """
        Merges neighbouring clusters until all sensitive data are l-diverse
        :param data_base_throw: the list of clusters not satisfying l-diversity
        """
        
        if len(data_base_throw) >1:
            for i in range(int(len(data_base_throw)/2)):
                data_base_throw[i].data+=data_base_throw[i+1].data
                data_base_throw.pop(i+1)
            for data_piece in self.sensitive:
                for cluster in data_base_throw:
                    tmp=[]
                    for linea in cluster.data:
                        tmp.append(linea[f"{data_piece}"])
                    if len(np.unique(tmp)) >= self.l:
                        cluster.numberOfSensitiveLDiverse += 1
                    if cluster.numberOfSensitiveLDiverse == len(self.sensitive):
                        new_cluster = []
                        for linea in cluster.data:
                            new_cluster.append(linea)
                        self.data_base.append(new_cluster)
                        data_base_throw.remove(cluster)

            for cluster in data_base_throw:
                cluster.numberOfSensitiveLDiverse = 0

            self.remisage(data_base_throw)        

    def export(self):
        """
        Exports the database in csv format
        """
        null_line = {col: "NULL" for col in self.row}
        with open(self.file_name, 'w', newline='') as csvfile:
            spamwriter = csv.DictWriter(csvfile, self.data_base[0][0].keys() , delimiter=',')
            spamwriter.writeheader()
            for cluster in self.data_base:
                for linea in cluster:
                    spamwriter.writerow(linea)
                spamwriter.writerow(null_line)
        print("Exportation successful")