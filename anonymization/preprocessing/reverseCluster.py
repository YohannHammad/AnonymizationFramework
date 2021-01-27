import csv
from .generateBase import Database
from .utils import nameToLatLong


def reverse_cluser(cluster_file, out_file, db, table, position=[], speciacols=[], idcol="id"):
    raw_data = db.dumpTable(table)
    raw_data_dict = {line[idcol]:line for line in raw_data}
    result = []
    line_reversed = 0
    with open(cluster_file, "r", newline="") as f:
        read_data = csv.DictReader(f)
        null_line = {col: "NULL" for col in read_data.fieldnames}
        for line in read_data:
            if line[idcol] is '':
                result.append(null_line)
            else:
                raw = raw_data_dict[int(float(line[idcol]))]
                result.append({key: raw[key] if key in raw else val for key, val in line.items()})
                for poscol in position:
                    pos = nameToLatLong(raw[poscol])
                    result[-1][f"lat_{poscol}"] = pos[0]
                    result[-1][f"lon_{poscol}"] = pos[1]
                for special in speciacols:
                    special(raw, line, result)
            line_reversed+=1
            if line_reversed%1000==0:
                print(line_reversed, " lines reversed")

    with open(out_file, "w", newline="") as f:
        w = csv.DictWriter(f, result[0].keys())
        w.writeheader()
        w.writerows(result)
