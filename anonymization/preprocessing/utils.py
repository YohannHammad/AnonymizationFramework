import datetime
import difflib
import pickle
import random
import re
import numpy as np
import requests
import sklearn.cluster
import psycopg2
import pprint


def nameToLatLong(location, cache_file="cache/.location_cache"):
    if not hasattr(nameToLatLong, "cache"):
        try:
            class lbdclass:
                def __del__(self):
                    if hasattr(nameToLatLong, "cache") and hasattr(nameToLatLong, "open"):
                        with nameToLatLong.open(cache_file, "w+b") as f:
                            pickle.dump(nameToLatLong.cache, f)

            setattr(nameToLatLong, "saver", lbdclass())
            setattr(nameToLatLong, "open", open)
            with open(cache_file, "rb") as f:
                setattr(nameToLatLong, "cache", pickle.load(f))
        except (FileNotFoundError, EOFError):
            setattr(nameToLatLong, "cache", {})

    formated_loc_name = location.upper().replace("_", " ")

    if formated_loc_name in nameToLatLong.cache:
        return nameToLatLong.cache[formated_loc_name]

    r = requests.get("https://www.openstreetmap.org/geocoder/search_osm_nominatim", params={"query": formated_loc_name})
    if "data-lat" not in r.text:
        if len(nameToLatLong.cache) > 0:
            pos = random.choice(list(nameToLatLong.cache.values()))
            nameToLatLong.cache[formated_loc_name] = pos
            return pos
        return (-1, -1)
    split = r.text.split("\n")
    posline = split[1]
    pos = float(re.findall(r'data-lat="(-?\d+\.\d+)"', posline)[0]), float(
        re.findall(r'data-lon="(-?\d+\.\d+)"', posline)[0])
    nameToLatLong.cache[formated_loc_name] = pos
    return pos


def date_to_timestamp(date):
    date = datetime.datetime(date.year, date.month, date.day) if type(date) == datetime.date else date
    return date.replace(tzinfo=datetime.timezone.utc).timestamp()


def str_comparator_levenshtein(str1, str2):
    sep_pattern = ';|,|\*|\n| |\||/|\.|_'
    formated_str1, formated_str2 = "".join(sorted(re.split(sep_pattern, str1.lower()))), "".join(
        sorted(re.split(sep_pattern, str2.lower())))
    # formated_str1, formated_str2 = formated_str1[:min(len(formated_str1), len(formated_str2))], formated_str2[:min(len(formated_str1), len(formated_str2))]
    matrix = np.zeros((len(formated_str1) + 1, len(formated_str2) + 1))
    matrix[0] = range(len(formated_str2) + 1)
    matrix[:, 0] = range(len(formated_str1) + 1)
    for j in range(1, len(formated_str2) + 1):
        for i in range(1, len(formated_str1) + 1):
            cost = 0 if formated_str2[j - 1] == formated_str1[i - 1] else 1
            matrix[i, j] = min(matrix[i - 1, j - 1] + cost,
                               matrix[i, j - 1] + 1,
                               matrix[i - 1, j] + 1)
    res = matrix[len(formated_str1), len(formated_str2)]
    return res


def str_comparator_ratio(str1, str2):
    sep_pattern = ';|,|\*|\n| |\||/|\.|_'
    formated_str1, formated_str2 = "".join(sorted(re.split(sep_pattern, str1.lower()))), "".join(
        sorted(re.split(sep_pattern, str2.lower())))
    res = difflib.SequenceMatcher(None, formated_str1, formated_str2).ratio()
    return res


def medium_string(l):
    res = []
    sep_pattern = ';|,|\*|\n| |\||/|\.|_'
    total_len = 0
    for str in l:
        str = "".join(sorted(re.split(sep_pattern, str.lower())))
        total_len += len(str)
        for i, byte in enumerate(str):
            if len(res) <= i:
                res.append({})
            if byte not in res[i]:
                res[i][byte] = 0
            res[i][byte] += 1
    return ''.join([max(res[i], key=lambda bit: res[i][bit]) for i in range(total_len // len(l))])


def sortStringListBySimilarity(l, distance_function=str_comparator_levenshtein):
    wordlist = np.asarray(l)
    random.shuffle(wordlist)
    lev_similarity = -1 * np.array([[distance_function(w1, w2) for w1 in wordlist] for w2 in wordlist])
    widestdamping = True
    damping = 0.5
    clusters = {}
    while widestdamping:
        affprop = sklearn.cluster.AffinityPropagation(affinity="precomputed", damping=damping, random_state=None)
        affprop.fit(lev_similarity)
        damping_ok = False
        for cluster_id in np.unique(affprop.labels_):
            if cluster_id == -1:
                damping += (1 - damping) / 2
                break
            widestdamping = False
            cluster_name = wordlist[affprop.cluster_centers_indices_[cluster_id]]
            cluster = np.unique(wordlist[np.nonzero(affprop.labels_ == cluster_id)])
            clusters[cluster_name] = cluster

    return [elem for name in sorted(clusters) for elem in clusters[name]]


def sortStringListBySimilarityButFast(l, distance_function=str_comparator_levenshtein):
    str_med = medium_string(l)
    return sorted(l, key=lambda string: distance_function(string, str_med))


def sortStringListBySimilarityButVeryFast(l):
    sep_pattern = ';|,|\*|\n| |\||/|\.|_'
    return sorted(l, key=lambda string: "".join(sorted(re.split(sep_pattern, string.lower()))))


def GDAtoCSV(db, table, filename="export/export.csv", limit=None):
    conn = psycopg2.connect(
        host="db001.gda-score.org",
        database=db,
        user="gda-score_ro_user",
        password="")

    cur = conn.cursor()
    s = f"SELECT * FROM {table}" + "" if limit is None else f" LIMIT {limit}"
    sql = "COPY ({0}) TO STDOUT WITH CSV HEADER".format(s)
    with open(filename, "w") as out:
        cur.copy_expert(sql, out)


def printParam(f):
    def execf(*args, **kwargs):
        pprint.pprint(args)
        pprint.pprint(kwargs)
        return f(*args, **kwargs)

    return execf
