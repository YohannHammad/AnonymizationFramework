
#Generer la base de taxis

from faker import Faker
import sys
import mysql.connector
import random
import csv
from .utils import sortStringListBySimilarity, sortStringListBySimilarityButFast, sortStringListBySimilarityButVeryFast, nameToLatLong, date_to_timestamp
from datetime import timezone, datetime

class DBTYPES:
    @classmethod
    def __gentype(cls, name, capacity, pk, autoincrement):
        return name + (" " if capacity is None else f"({capacity}) ") + ("PRIMARY KEY " if pk else " ") + ("AUTO_INCREMENT" if autoincrement else "")

    @classmethod
    def INTEGER(cls, capacity=None, pk=False, autoincrement=False):
        return DBTYPES.__gentype("INTEGER", capacity, pk, autoincrement)

    @classmethod
    def TEXT(cls, capacity=None, pk=False, autoincrement=False):
        return DBTYPES.__gentype("TEXT", capacity, pk, autoincrement)

    @classmethod
    def DATETIME(cls, capacity=None, pk=False, autoincrement=False):
        return DBTYPES.__gentype("DATETIME", capacity, pk, autoincrement)

    @classmethod
    def DATE(cls, capacity=None, pk=False, autoincrement=False):
        return DBTYPES.__gentype("DATE", capacity, pk, autoincrement)

    @classmethod
    def REAL(cls, capacity=None, pk=False, autoincrement=False):
        return DBTYPES.__gentype("REAL", capacity, pk, autoincrement)





class Database(DBTYPES):
    def __init__(self, name, host, user, password, port=3306):
        if name=="":
            print("Base name should not be empty", file=sys.stderr)
            Database.__del__ =  lambda x: None
            exit(1)
        self.realname = f"{user}_{name}"
        self.cnx = mysql.connector.connect(user=user, password=password, host=host, database="")
        self.cursor = self.cnx.cursor()
        self.cursor.execute("show databases")
        self.isNewDb = self.realname not in [db[0] for db in self.cursor]
        if self.isNewDb:
            print(f"Database {name} does not exist. Creating it")
            self.cursor.execute(f"CREATE DATABASE {self.realname}")
            self.cursor.execute(f"USE {self.realname}")
            self.structure = {}
        else:
            self.cursor.execute(f"USE {self.realname}")
            self._buildStruct()
        self.structure_change = {}

    def __del__(self):
        try:
            self.cursor.close()

            self.cnx.close()
        except:
            pass

    def _buildStruct(self):
        self.cursor.execute("SHOW TABLES")
        self.structure = {table[0]: {elem[0]: elem[1:] for elem in self.cursor.execute(f"DESC {table[0]}") or self.cursor} for table in self.cursor.fetchall()}

    def isCreating(self):
        return self.isNewDb

    def getTables(self):
        return self.structure.keys()

    def createTable(self, table_name):
        if table_name in self.structure:
            print(f"Can't create table {table_name}. It already exist")
            return
        self.structure_change[table_name] = {}

    def dropTable(self, table_name):
        if table_name not in self.structure:
            print(f"Can't drop table {table_name}. It don't exist")
            return
        self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        del self.structure[table_name]

    def addColumn(self, table_name, col_name, col_type, if_not_exist = True):
        if table_name not in self.structure and table_name not in self.structure_change:
            print(f"Can't add column '{col_name}' on table '{table_name}' table don't exist")
            return

        if if_not_exist and table_name in self.structure and col_name in self.structure[table_name]:
            print(f"The col '{col_name}' already exist in the table '{table_name}' please delete it before or set the if_not_exist flag to False")
            return

        if table_name not in self.structure_change:
            self.structure_change[table_name] = {}
        self.structure_change[table_name][col_name] = col_type

    def commit(self):
        request_string = ""
        for new_table in self.structure_change.keys() - self.structure.keys():
            if len(self.structure_change[new_table]) == 0:
                print(f"A table need to have at least one primary key column for {new_table}")
                return
            request_string += f"CREATE TABLE {new_table}({','.join([col + ' ' + self.structure_change[new_table][col] for col in self.structure_change[new_table]])});"
        for alter_table in self.structure_change.keys() & self.structure.keys():
            for col in self.structure_change[alter_table]:
                request_string+=f"ALTER TABLE {alter_table}  ADD COLUMN {col} {self.structure_change[alter_table][col]}:"

        self.cursor.execute(request_string)
        self._buildStruct()
        self.structure_change = {}

    def generateMockData(self, table_name, generator, number_of_generation, also_generate_id=False):
        if table_name not in self.structure:
            print(f"Table {table_name} do not exist")
            return

        data = next(generator)
        missing = [field for field in self.structure[table_name].keys() - data.keys() if self.structure[table_name][field][2] != "PRI" or also_generate_id]
        if len(missing)>0:
            print(f"Error fields {missing} aren't generated by the generator")
            return


        cols = [field for field in self.structure[table_name].keys() if self.structure[table_name][field][2] != "PRI" or also_generate_id]
        req = f"INSERT INTO {table_name}({','.join(cols)}) VALUES "
        placeholder = f"({','.join(['%s' for i in range(len(cols))])})"
        values = []

        def genappend():
            yield data
            while True:
                yield next(generator)

        generator_2 = genappend()
        req_cpy = req
        for i in range(number_of_generation):
            data = next(generator_2)
            values += [data[col] for col in cols]
            req+=placeholder
            if i%10000==0:
                print("Commit " + str(i))
                self.cursor.execute(req, values)
                self.cnx.commit()
                req = req_cpy
                values = []
            elif i!=number_of_generation-1:
                req += ","
        self.cursor.execute(req, values)
        self.cnx.commit()

    def dumpTable(self, table_name, limit=None):
        if table_name not in self.structure:
            print(f"Can't fetch data from {table_name} it don't exist")
            return
        c = self.cnx.cursor(dictionary=True)
        c.execute(f"SELECT * FROM {table_name} " + (f"LIMIT {limit}" if limit is not None else ""))
        res =  c.fetchall()
        c.close()
        return res

    def toCSV(self, table, filename):
        """
        Export a table to csv format
        :param table: The name of the table to export
        :param filename: The file to create
        :return:
        """
        if table not in self.structure:
            print(f"Can't convert {table} it don't exist")
            return
        data = self.dumpTable(table)
        keys = data[0].keys()
        with open(filename, mode="w", newline="") as file:
            dict_writer = csv.DictWriter(file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)

    def fromCSV(self, table_name, file,  desc, transform={}, renames={}):
        """
        Create a table from a csv file
        :param table_name: The name of the table to create
        :param file: The path to the csv file
        :param desc: The description of the columns with the columns name matching the csv header and the values being from the DBTYPE class
        :param transform: A dictionnary of function to apply on field before importing data. The dictionnay have columns name as key and a function that take the row as parameter and return the value for the field to transform
        :return:
        """
        with open(file, mode="r", newline="") as file:
            self.createTable(table_name)
            for col in desc:
                self.addColumn(table_name, renames[col] if col in renames else col, desc[col])
            self.commit()
            data = list(csv.DictReader(file))
            self.generateMockData(table_name, ({col if col not in renames else renames[col]:transform[col](elem) if col in transform else val for col, val in elem.items()} for elem in data), len(data)-1)






    def kannonbase(self, table, k, DS, QUID, DID, dropTableIfExiste = True):
        """
        :param self: Objet Database qui contient la table à annoonimiser
        :param table: Le nom de la table à annonimiser
        :param k: Le nombre d'individus par groupe
        :param DS: Une liste des attributs sensible
        :param QUIDs: Une liste de liste, les sous liste sont les QuasiIdentifiants
        :param DID: Une liste d'attibut étant directement identifiant, c'est attributs serons supprimer
        :return:
        """
        new_table_name = f"kannonbase_{table}"
        if new_table_name in self.structure:
            if dropTableIfExiste:
                self.cursor.execute("DROP TABLE " + new_table_name)
                self._buildStruct()
            else:
                raise Exception("Table " + new_table_name + "already exist and the drop is set to false")
        raw_content = self.dumpTable(table)
        new_table_struct = self.structure[table]
        for direct_id in DID:
            if direct_id in new_table_struct: del new_table_struct[direct_id]

        raw_content.sort(key=lambda x:tuple(x[quid].lower() if type(x[quid]) is str else x[quid] for quid in QUID))

        grps = []
        reste = []
        for i in range(0, len(raw_content), k):
            for ds in DS:
                shuffle_ds = []
                for elem in raw_content[i:i+k]:
                    shuffle_ds.append(elem[ds])
                random.shuffle(shuffle_ds)
                for elem in raw_content[i:i+k]:
                    elem[ds] = shuffle_ds.pop(0)
            if len(raw_content[i:i+k])<k:
                reste.extend(raw_content[i:i+k])
            else:
                grps.append(raw_content[i:i+k])

        self.createTable(new_table_name)
        hasId = False
        for col in new_table_struct:
            self.addColumn(new_table_name, col, new_table_struct[col][0] + (" PRIMARY KEY" if new_table_struct[col][2] == "PRI" else ""))
            if new_table_struct[col][2] == "PRI":
                hasId = True
        if not hasId:
            self.addColumn(new_table_name, "auto_id", DBTYPES.INTEGER(pk=True, autoincrement=True))
        self.commit()
        self.generateMockData(new_table_name, (entry for grp in grps for entry in grp), len(raw_content)-len(reste)-1)




    def preprocessTable(self, table, ignore=[], indexation=[], indexation_rate=10,  position=[], str_sorting_function=sortStringListBySimilarity, recompute=False, limit=None,  **special_col):
        """
        Effetue le preprocessing sur une table dans l'optique de la transformée entièrement en valeur numérique pour l'algorithme de mondrian.
        L'algo suit l'arbre de décision suivant : https://drive.google.com/file/d/15Vu7wAjSvem0tW_bykXV6GV7dD0fPTQI/view?usp=sharing
        :param table:           Le nom de la table sur laquelle effectuer le preprocessing
        :param ignore:          Une liste de colonnes (potentiellement vide) qui ne doit pas se retrouver dans le résultat.
                                peut être utile pour des colonnes qui fonctionnent par pair. Par example sur une table avec une adresse et un zip on peut
                                exlure l'un des deux et utiliser le special_col pour prendre les deux en compte dans un seul champ. Peut aussi permetre d'exlure des DID et économiser du temp de traitement.

        :param indexation:      Une list des champs qui doivent simplement être indéxé par valeur (les valeur sont indépendante les une des autres ou n'ont que peut de valeur possible.
        :param indexation_rate: Determine le nombre de valeur différente maximal possible pour qu'une colone textuelle soit détérminée comme à indéxer par l'arbre de décision
                                (peut être un entier ou un float pour un pourcentage sur l'ensemble des données)
        :param position:        Décris les champs texte qui devraient être traiter comme des positions
        :str_sorting_function:  Une fonction qui prend une liste de chaine de charactère et qui retourne une version triée de sorte à ce que les chaine proche entre elle dans la liste aient une signification commune
        :recompute:             Un booléan qui indique si l'on doit recalculer le préprocessing si il à déjà été fait.
        :limit:                 Nombre de lignes à annonimiser, None indique de prendre toute la tabe sinon un nombre maximum de ignes sééctionnée aéatoirement.
        :param special_col:     Possibilitée de passer des paramètre nomer avec le nom des colone ou la valeur est une fonction custom qui prend en entrée la ligne complète (sous forme de dictionnaire {"colone":valeur}
                                et retourne une valeur numérique pour la collone concernée.
        :return:                Le tuple ([liste des donnée clair], [liste des donnée préprocessing])
        """
        if table not in self.structure:
            print(f"preprocessing table {table} not found")
            exit()
        output_table_name = f"preproceced_{table}"
        if output_table_name in self.structure and not recompute:
            return (self.dumpTable(table), self.dumpTable(output_table_name))

        #Initialisation
        print("Preprocessing : INITIALISATION")
        table_struct = {key:value for key,value in self.structure[table].items() if key not in ignore}
        indexations_distinct = {name:set() for name in table_struct if ("text" in table_struct[name] or name in indexation) and name not in special_col}
        min_max = dict()
        def minmaxup(col_name, value):
            if col_name not in min_max:
                min_max[col_name] = [float("inf"), float("-inf")]
            if value > min_max[col_name][1]:
                min_max[col_name][1] = value
            elif value < min_max[col_name][0]:
                min_max[col_name][0] = value
        raw_data = self.dumpTable(table)
        if limit is not None:
            random.shuffle(raw_data)
            raw_data = raw_data[:limit]
        auto_index_max_count = indexation_rate if isinstance(indexation_rate, int) else int(indexation_rate * len(raw_data))

        print("Preprocessing : PREPREPROCESSING")
        #PrePreprocessing pour indexation colone
        for data_line in raw_data:
            for col in indexations_distinct:
                indexations_distinct[col].add(data_line[col])
        indexations_distinct = {col:list(val) for col,val in indexations_distinct.items()}
        sorted_field_for_str_distance = []

        preproceced_data = []

        print("Preprocessing : PREPROCESSING")
        #Preprocessing
        for data_line in raw_data:
            preproceced_line = {}
            for field, value in data_line.items():
                value_computed = None
                if field in ignore:
                    continue
                if field in special_col:
                    value_computed = special_col[field](data_line)
                elif field in indexation:
                    value_computed = indexations_distinct[field].index(value)
                elif "int" in table_struct[field][0]:
                    value_computed = value
                elif "real" in table_struct[field][0] or "double" in table_struct[field][0]:
                    value_computed = value
                elif "date" in table_struct[field][0]:
                    value_computed = date_to_timestamp(value)
                elif "datetime" in table_struct[field][0]:
                    value_computed = date_to_timestamp(value)
                elif "text" in table_struct[field][0]:
                    if len(indexations_distinct[field]) <= auto_index_max_count:
                        value_computed = indexations_distinct[field].index(value)
                    elif field in position:
                        value_computed = nameToLatLong(value)
                    else:
                        #Tri par distance entre les nom
                        if field not in sorted_field_for_str_distance:
                            print("Sorting " + field)
                            indexations_distinct[field] = str_sorting_function(indexations_distinct[field])
                            print("End Sorting " + field)
                            sorted_field_for_str_distance.append(field)
                        value_computed = indexations_distinct[field].index(value)
                else:
                    print(f"preprocessing field {field} have unknow type '{table_struct[field][0]}'. please go hit theodore that forget to implent this type or pass a function with {field} as a name attribute that transform this col to a number")
                    exit()

                if type(value_computed) in (tuple, set, frozenset, list):
                    fields = [f"lat_{field}", f"lon_{field}", *range(len(value_computed))] if field in position else range(len(value_computed))
                    for fildname, fieldvalue in zip(fields, value_computed):
                        minmaxup(fildname, fieldvalue)
                        preproceced_line[fildname] = fieldvalue
                else:
                    minmaxup(field, value_computed)
                    preproceced_line[field] = value_computed
            preproceced_data.append(preproceced_line)

        print("Preprocessing : NORMALISATION")
        #Normalisation entre 0 et 1
        for preproceced_line in preproceced_data:
            for field, value in preproceced_line.items():
                if field not in table_struct or table_struct[field][2] != "PRI":
                    if (min_max[field][1]-min_max[field][0]) != 0:
                        preproceced_line[field] = (value - min_max[field][0])/(min_max[field][1]-min_max[field][0])
                    else:
                        preproceced_line[field] = 0.5
                    preproceced_line[field] += 1

        print("Preprocessing : CREATING_OUT_TABLE")
        if output_table_name in self.structure:
            self.dropTable(output_table_name)
        self.createTable(output_table_name)
        if len(preproceced_data)>0:
            for col in preproceced_data[0]:
                pri = col in table_struct and table_struct[col][2] == "PRI"
                self.addColumn(output_table_name, col, DBTYPES.REAL(pk=pri))
            self.commit()
            self.generateMockData(output_table_name, (val for val in preproceced_data), len(preproceced_data), also_generate_id=True)
        return (output_table_name, raw_data, preproceced_data)