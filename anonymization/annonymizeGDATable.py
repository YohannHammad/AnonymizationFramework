import anonymization.preprocessing as preprocessing
import anonymization.processing as processing
import anonymization.postprocessing as postprocessing
from anonymization.processing.Mondrian import Mondrian
from anonymization.preprocessing.reverseCluster import reverse_cluser
from anonymization.postprocessing.generalization import Generalization
from anonymization.processing.l_div_naive import l_div_naive
import os
from anonymization.preprocessing import printParam


def annonymizeGDATable(username,
                       password,
                       dbname,
                       tablename,
                       gda_dbname,
                       gda_tablename,
                       table_structure,
                       ignore_fields,
                       position_fields,
                       index_field,
                       quid_list,
                       sensitive_list,
                       k,
                       l,

                       postion_in_lat_lon=[],
                       gda_rawfile="export/raw_gda_{}_{}.csv",
                       preproceceed_file="export/preproceceed_{}_{}.csv",
                       proceceed_file="export/proceceed_{}_{}.csv",
                       clear_preprocecedd_file="export/clear_proceceed_{}_{}.csv",
                       postprocecedd_file="export/postproceceed_{}_{}.csv",
                       gda_rawfile_limit=None,
                       gda_raw_transform={},
                       indexation_rate=10,
                       str_sort_function=preprocessing.sortStringListBySimilarity,
                       preprocecing_transform_columns={},
                       show_clusers = False,
                       cluster_transforms=[],
                       local_db_host="localhost",
                       local_db_port=3306,
                       use_cache=True,
                       local_table_already_created=False,
                       enable_log=False,
                       pk_colname="id"):
    """
    Allow to annonimize a table of the gdaframework
    :param username: The username to connect to the local database
    :param password: The password matching the username parameter
    :param dbname: The name of the local database to use
    :param tablename: The name of the localtable to use
    :param gda_dbname: The name of the gda database that contain the table to annonimize
    :param gda_tablename: The name of the gda table to annonymize
    :param table_structure: A dictionnary with the columnsname as key and the types as value (types come from the DBTYPES). Do not use a primary key it will be added automatically.
    :param ignore_fields: A list of fields that we should ignore during the process (mainly the direct ids) can be None
    :param position_fields: A list of fields that should be computed as position and transform in latitude and longitude. Can be None
    :param index_field: A list of fields that should be annonimized using indexion. Can be None
    :param quid_list: A list that contain the quid columns of the table
    :param sensitive_list: A list that contain the sensitive columns of the table
    :param k: The value of k to use to generate clusters
    :param l: The value of the minimal diversity of sensitive values in each cluster

    :param postion_in_lat_lon: A list of tuple that give the lattitude and longitude cols.
    :param gda_rawfile: The file where the raw content of the dumped gda file will be exported can use a string placeholder in the name to put the database and table name
    :param preproceceed_file: The file where the raw content of the preproceceed table will be saved. Can use placeholders for the base and table name and can also be None to not export the preproceceed date into a file.
    :param proceceed_file: The file where the generated clusters are saved
    :param clear_preprocecedd_file: The file where the generated clusters are reversed in their real values.
    :param postprocecedd_file: The file where the generalised clusters are stored. Can use placeholders for the base and table name.
    :param gda_rawfile_limit: The maximum number of line to download from the gda raw database. Can be None to use all of it
    :param gda_raw_transform: A dictionnary that have column name as key and function as value. The functions take a full line of data and return a value for the corresponding column.
                              Each field supplied is transformed using the function before the creation of the local table.
    :param indexation_rate: The maximum number of distinct values in a column to index the field. Can be integer for a fixed count of value or a float between 0 and 1 for a percentage of the rows count. The column in the indexation parameter ignore this
    :param str_sort_function: The function to use to sort string for the automatic indexation this function take a list of string and a distance function as parameter
    :param preprocecing_transform_columns: A dictionnary that have the column name as key and a function that take a complete line and return a numeric value for the corresponding key
    :param show_clusers: A boolean that will log or not the cluters
    :param cluster_transforms: A list of function that take tree arguments the raw line the line and the result and edit it.
    :param local_db_host: The host to connect to access the local database
    :param local_db_port: The port to connect to access the local database host

    :param pk_colname: The name of the column that will be the primary key
    :param use_cache: Indicate if we shoud use the cache that we already have
    :param local_table_already_created: Say if the local table is already generated the only use it and ignore the GDA
    :param enable_log: Enable or disable the generation for logs. Can generate a lot of data.
    :return:
    """
    db = preprocessing.Database(dbname, local_db_host, username, password)
    gda_rawfile = gda_rawfile.format(gda_dbname, gda_tablename)
    raw_gda_data_downloaded=False
    if not use_cache or os.path.exists(gda_rawfile):
        if not local_table_already_created:
            preprocessing.GDAtoCSV(gda_dbname, gda_tablename, filename=gda_rawfile, limit=None)
        else:
            db.toCSV(gda_tablename, gda_rawfile)
        raw_gda_data_downloaded = True

    if (tablename in db.getTables() and not use_cache) or raw_gda_data_downloaded:
        db.dropTable(tablename)
        renames = {}
        for lat_col,lon_col in postion_in_lat_lon:
            table_structure[f"lat_{lat_col}"] = table_structure[lat_col]
            table_structure[f"lon_{lon_col}"] = table_structure[lon_col]
            renames[lat_col] = f"lat_{lat_col}"
            renames[lon_col] = f"lon_{lon_col}"
            del table_structure[lat_col]
            del table_structure[lon_col]

        db.fromCSV(tablename, gda_rawfile, {**table_structure, **{pk_colname:preprocessing.DBTYPES.INTEGER(pk=True, autoincrement=True)}}, transform=gda_raw_transform, renames=renames)

    print("Preprocecing")
    preproceceed_table, raw_data, preprocess_data = db.preprocessTable(tablename,
                                                                       ignore=ignore_fields or [],
                                                                       indexation=index_field or [],
                                                                       indexation_rate=indexation_rate,
                                                                       position=position_fields or [],
                                                                       str_sorting_function=str_sort_function,
                                                                       recompute=not use_cache or raw_gda_data_downloaded,
                                                                       **preprocecing_transform_columns)
    preproceceed_file = None if preproceceed_file is None else preproceceed_file.format(dbname, tablename)
    if preproceceed_file:
        db.toCSV(preproceceed_table, preproceceed_file)

    #Mondrian_K-anom
    print("Mondrian")
    for elem in quid_list:
        if elem in position_fields:
            quid_list.remove(elem)
            quid_list.append(f"lat_{elem}")
            quid_list.append(f"lon_{elem}")
    for elem in sensitive_list:
        if elem in position_fields:
            sensitive_list.remove(elem)
            sensitive_list.append(f"lat_{elem}")
            sensitive_list.append(f"lon_{elem}")

    for lat_col, lon_col in postion_in_lat_lon:
        if lat_col in quid_list:
            quid_list[quid_list.index(lat_col)] = f"lat_{lat_col}"
        if lon_col in quid_list:
            quid_list[quid_list.index(lon_col)] = f"lon_{lon_col}"
    mondrian_fields = [pk_colname] + quid_list + sensitive_list
    #print(mondrian_fields)
    datas_f  = [[line[col] for col in mondrian_fields] for line in preprocess_data]

    mondrian = Mondrian(k, datas_f, [i for i in range(1,len(quid_list)+1)], step=False, log=enable_log)
    mondrian.run()
    if show_clusers:
        mondrian.show_final()
    proceceed_file = proceceed_file.format(dbname, tablename)
    mondrian.export_result_to_csv(mondrian_fields, proceceed_file)

    clear_preprocecedd_file = clear_preprocecedd_file.format(dbname, tablename)
    print("Reversing clusters")
    reverse_cluser(proceceed_file, clear_preprocecedd_file, db, tablename, position=position_fields, speciacols=cluster_transforms, idcol=pk_colname)
    
    #L-diversity naive
    remisage= True
    table_div = l_div_naive(l,clear_preprocecedd_file, sensitive_list, quid_list, [pk_colname])
    table_div.diversification(remisage)
    table_div.export()
    
    #Postprocessing
    dezoom = False
    postprocecedd_file = postprocecedd_file.format(dbname, tablename)
    table = Generalization(k,clear_preprocecedd_file, postprocecedd_file, quid_list)
    table.generalize(dezoom)
    table.export()
    








