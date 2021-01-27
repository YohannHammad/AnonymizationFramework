# -*-coding: utf-8 -*-

from statistics import median
import matplotlib.pyplot as plt
import random
from time import time
import pandas as pd
from .Logger import Logger


class Partition:
	def __init__(self, datas):
		self.datas = datas

	def __len__(self):
		return len(self.datas)


class Mondrian:
	def __init__(self, k, datas, dimensions, step=False, log=False):
		"""
		Instanciation de Mondrian
		:param k: Valeur de K pour le k-anonymat
		:param datas: Jeu de données dans un tableau à deux dimensions
		:param dimensions: Index des quasi-identifiants
		:param step: Faut-il exécuter l'algorithme étape par étape (en appuyant sur Entrer dans la console)
		:param log: Faut-il écrire les logs dans un fichier de sortie
		"""
		self.k = k
		self.datas = datas
		self.dimensions = dimensions
		self.result = []
		self.step = step
		self.width = {}
		self.mins = {}
		self.lost_data = 0
		self.logger = Logger("cache/logs" + str(time()) + ".txt", log)
		self.trash = []

	def run(self):
		"""
		Exécution de Mondrian.
		"""
		msg = "K = {}\n".format(self.k)
		msg += "Nombre de données = {}\n".format(len(self.datas))
		msg += "Données :\n{}\n==================".format(self.datas)
		self.logger.write(msg)

		# On récupère la "width" de chaque dimension et la valeur minimale
		# Utile pour le calcul des "widest normalized range"
		for dim in self.dimensions:
			self.datas.sort(key=lambda datas: datas[dim])
			self.width[dim] = self.datas[-1][dim] - self.datas[0][dim]
			self.mins[dim] = self.datas[0][dim]

		# Initialision la première partition et exécution de l'algorithme
		based_partition = Partition(self.datas)
		self.anonymize(based_partition)

	def choose_dimension(self, partition):
		"""
		La dimension choisie sera celle qui aura la plus large range de valeurs (normalisées entre 0 et 1)
		// One heuristic, used in our implementation, chooses the dimension with the widest (normalized)
		range of values
		:param partition: La partition dont il est nécessaire de choisir une dimension
		"""
		maxWidth = -1
		dim = -1
		for i in self.dimensions:
			width = self.normalized_width(partition, i)
			self.logger.write("[Dimension] Width {} : {}".format(i, width))
			if width > maxWidth:
				dim = i
				maxWidth = width
		self.logger.write("[Dimension] Largest width : {}".format(maxWidth))
		return dim

	def frequency_set(self, partition, dim):
		"""
		The frequency set of attribute A for partition P
		is the set of unique values of A in P, each paired
		with an integer indicating the number of times it appears
		in P
		:param partition: La partition qui contient les données
		:param dim: La dimension de travail
		"""
		fs = {}
		for i in partition.datas:
			if i[dim] not in fs:
				fs[i[dim]] = 0
			fs[i[dim]] += 1
		return fs

	def normalized_width(self, partition, dim):
		"""
		Normalisation d'un ensemble de données entre 0 et 1
		// One heuristic, used in our implementation, chooses the dimension with the widest (normalized)
		range of values
		:param partition: La partition qui contient les données
		:param dim: La dimension de travail
		"""
		datas = [partition.datas[i][dim] for i in range(len(partition))]
		datas.sort()
		datasNormalized = [(x - self.mins[dim]) / self.width[dim] for x in datas]
		width = datasNormalized[-1] - datasNormalized[0]
		return width

	def recoding(self, partition):
		"""
		Save clusters
		"""
		self.logger.write("[Recoding] {}".format(partition.datas))
		self.result.append(partition.datas)

	def find_median(self, partition, fs, dim):
		"""
		Calcul de la split val en fonction de la fréquence d'apparition des données et de la dimension
		// One strategy used for obtaining uniform occupancy was median partitioning
		:param partition: La partition qui contient les données
		:param fs: Fréquence d'apparition des données de la dimension dim
		:param dim: La dimension de travail
		"""
		splitval = 0
		self.logger.write("[Median] fs : {}".format(fs))

		to_compute = [k for k, v in fs.items() for i in range(v)]
		self.logger.write("[Median] cm : {}".format(to_compute))

		med = median(to_compute)
		self.logger.write("[Median] med : {}".format(med))
		partition.datas.sort(key=lambda datas: datas[dim])
		if med in fs:
			v = fs[med]//2
			c = 0

			for i in range(len(partition.datas)):
				if (partition.datas[i][dim] == med):
					splitval = i
					c += 1
					if c == v: break
		else:
			for i in range(len(partition.datas)):
				if (partition.datas[i][dim] <= med):
					splitval = i

		self.logger.write("[Median] Splitval : {}".format(splitval + 1))
		return splitval + 1

	def show_graph(self):
		"""
		Nuage de points : ne pas utiliser si plus de 2 dimensions
		"""
		r = lambda: random.randint(0, 255)
		x = []
		y = []

		for i in self.result:
			color = '#%02X%02X%02X' % (r(), r(), r())
			for j in i:
				x.append(j[0])
				y.append(j[1])
				plt.scatter(j[0], j[1], c=[color])

		plt.xlabel('x')
		plt.ylabel('y')
		plt.show()

	def show_final(self):
		"""
		Afficher les clusters finaux ainsi que le nombre de données perdues
		"""
		msg = "==================\nClusters :\n"
		global nb_cluster
		for nb_cluster in range(len(self.result)):
			msg += "{}. (k = {}) {}\n".format(nb_cluster, len(self.result[nb_cluster]), self.result[nb_cluster])
		self.logger.write(msg)

	def export_result_to_csv(self, names, out=-1):
		"""
		Exporter les clusters au format CSV ~ un saut de ligne a été ajouté pour différencier les clusters (k variable)
		:param names: Nom des colonnes
		:param out: Nom du fichier de sortie, export-{k}.txt par défaut
		"""
		if out == -1:
			out = "export-{}.txt".format(self.k)

		datas = []
		for element in self.result:
			for cluster in element:
				datas.append(cluster)
			line_break = [None] * len(datas[-1])
			datas.append(line_break)

		pd.DataFrame(datas).to_csv(out, sep=',', header=names, index=None)

	def trash_datas(self, datas):
		"""
		Stockage des données perdues (inutile pour le moment)
		:param datas: Le tableau des données à stocker
		"""
		for data in datas:
			self.trash.append(data)

	def anonymize(self, partition, dim=-1):
		"""
		Algorithme principal basé sur le pseudo-code de LeFevre, DeWitt et Ramakrishnan
		:param partition: Partition de travail
		:param dim: Si différent de -1, spécification manuelle de la dimension de travail
		"""
		if len(partition) == self.k:
			self.recoding(partition)
		else:
			if self.step:
				input()

			if dim == -1:
				dim = self.choose_dimension(partition)

			partition.datas.sort(key=lambda datas: datas[dim])
			self.logger.write("[Anonymize] datas : {}".format("..."))
			self.logger.write("[Anonymize] dimension : {}".format(dim))
			fs = self.frequency_set(partition, dim)
			splitVal = self.find_median(partition, fs, dim)

			lhs = Partition(partition.datas[:splitVal])
			rhs = Partition(partition.datas[splitVal:])
			self.logger.write("[Anonymize] lhs ({}) {}".format(len(lhs), lhs.datas))
			self.logger.write("[Anonymize] lhs ({}) {}".format(len(rhs), rhs.datas))

			if len(lhs) < self.k or len(rhs) < self.k:
				self.logger.write("[Anonymize] Len < k ({})".format(len(partition)))
				self.recoding(partition)
			else:
				self.anonymize(lhs)
				self.anonymize(rhs)
