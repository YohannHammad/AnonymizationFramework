from anonymization.annonymizeGDATable import *
from anonymization.preprocessing import *
import datetime
table_structure = {"uid":DBTYPES.INTEGER(),
                  "year":DBTYPES.INTEGER(),
                  "datanum":DBTYPES.TEXT(),
                  "serial": DBTYPES.INTEGER(),
                  "hhwt" : DBTYPES.TEXT(),
                  "gq": DBTYPES.INTEGER(),
                  "pernum" : DBTYPES.INTEGER(),
                  "perwt" : DBTYPES.INTEGER(),
                  "famsize" : DBTYPES.INTEGER(),
                  "nchild" : DBTYPES.INTEGER(),
                  "nchlt5" : DBTYPES.INTEGER(),
                  "nsibs" : DBTYPES.INTEGER(),
                  "relate" : DBTYPES.INTEGER(),
                  "related" : DBTYPES.INTEGER(),
                  "sex" : DBTYPES.INTEGER(),
                  "age" : DBTYPES.INTEGER(),
                  "birthqtr" : DBTYPES.INTEGER(),
                  "marst" : DBTYPES.INTEGER(),
                  "birthyr" : DBTYPES.INTEGER(),
                  "marrno" : DBTYPES.INTEGER(),
                  "yrmarr" : DBTYPES.INTEGER(),
                  "race" : DBTYPES.INTEGER(),
                  "raced" : DBTYPES.INTEGER(),
                  "hispan" : DBTYPES.INTEGER(),
                  "hispand" : DBTYPES.INTEGER(),
                  "bpl" : DBTYPES.INTEGER(),
                  "bpld" : DBTYPES.INTEGER(),
                  "citizen" : DBTYPES.INTEGER(),
                  "yrnatur" : DBTYPES.INTEGER(),
                  "yrimmig" : DBTYPES.INTEGER(),
                  "yrsusa1" : DBTYPES.INTEGER(),
                  "language" : DBTYPES.INTEGER(),
                  "languaged" : DBTYPES.INTEGER(),
                  "speakeng" : DBTYPES.INTEGER(),
                  "racamind" : DBTYPES.INTEGER(),
                  "racasian" : DBTYPES.INTEGER(),
                  "racblk" : DBTYPES.INTEGER(),
                  "racpacis" : DBTYPES.INTEGER(),
                  "racwht" : DBTYPES.INTEGER(),
                  "racother" : DBTYPES.INTEGER(),
                  "hcovany" : DBTYPES.INTEGER(),
                  "hcovpriv" : DBTYPES.INTEGER(),
                  "hinsemp" : DBTYPES.INTEGER(),
                  "hinspur" : DBTYPES.INTEGER(),
                  "hinstri" : DBTYPES.INTEGER(),
                  "hcovpub" : DBTYPES.INTEGER(),
                  "hinscaid" : DBTYPES.INTEGER(),
                  "hinscare" : DBTYPES.INTEGER(),
                  "hinsva" : DBTYPES.INTEGER(),
                  "hinsihs" : DBTYPES.INTEGER(),
                  "school" : DBTYPES.INTEGER(),
                  "educ" : DBTYPES.INTEGER(),
                  "educd" : DBTYPES.INTEGER(),
                  "gradeatt" : DBTYPES.INTEGER(),
                  "gradeattd" : DBTYPES.INTEGER(),
                  "schltype" : DBTYPES.INTEGER(),
                  "degfield" : DBTYPES.INTEGER(),
                  "degfieldd" : DBTYPES.INTEGER(),
                  "degfield2" : DBTYPES.INTEGER(),
                  "degfield2d" : DBTYPES.INTEGER(),
                  "empstat" : DBTYPES.INTEGER(),
                  "empstatd" : DBTYPES.INTEGER(),
                  "labforce" : DBTYPES.INTEGER(),
                  "occ" : DBTYPES.INTEGER(),
                  "ind" : DBTYPES.INTEGER(),
                  "classwkr" : DBTYPES.INTEGER(),
                  "classwkrd" : DBTYPES.INTEGER(),
                  "wkswork2" : DBTYPES.INTEGER(),
                  "uhrswork" : DBTYPES.INTEGER(),
                  "absent" : DBTYPES.INTEGER(),
                  "looking" : DBTYPES.INTEGER(),
                  "availble" : DBTYPES.INTEGER(),
                  "wrkrecal" : DBTYPES.INTEGER(),
                  "workedyr" : DBTYPES.INTEGER(),
                  "inctot" : DBTYPES.INTEGER(),
                  "ftotinc" : DBTYPES.INTEGER(),
                  "incwage" : DBTYPES.INTEGER(),
                  "incbus00" : DBTYPES.INTEGER(),
                  "incss" : DBTYPES.INTEGER(),
                  "incwelfr" : DBTYPES.INTEGER(),
                  "incinvst" : DBTYPES.INTEGER(),
                  "incretir" : DBTYPES.INTEGER(),
                  "incsupp" : DBTYPES.INTEGER(),
                  "incother" : DBTYPES.INTEGER(),
                  "incearn" : DBTYPES.INTEGER(),
                  "poverty" : DBTYPES.INTEGER(),
                  "occscore" : DBTYPES.INTEGER(),
                  "migrate1" : DBTYPES.INTEGER(),
                  "migrate1d" : DBTYPES.INTEGER(),
                  "migplac1" : DBTYPES.INTEGER(),
                  "migpuma1" : DBTYPES.INTEGER(),
                  "movedin" : DBTYPES.INTEGER(),
                  "vetdisab" : DBTYPES.INTEGER(),
                  "diffrem" : DBTYPES.INTEGER(),
                  "diffphys" : DBTYPES.INTEGER(),
                  "diffmob" : DBTYPES.INTEGER(),
                  "diffcare" : DBTYPES.INTEGER(),
                  "diffsens" : DBTYPES.INTEGER(),
                  "diffeye" : DBTYPES.INTEGER(),
                  "diffhear" : DBTYPES.INTEGER(),
                  "vetstat" : DBTYPES.INTEGER(),
                  "vetstatd" : DBTYPES.INTEGER(),
                  "vet01ltr" : DBTYPES.INTEGER(),
                  "pwstate2" : DBTYPES.INTEGER(),
                  "pwpuma00" : DBTYPES.INTEGER(),
                  "tranwork" : DBTYPES.INTEGER(),
                  "carpool" : DBTYPES.INTEGER(),
                  "riders" : DBTYPES.INTEGER(),
                  "trantime" : DBTYPES.INTEGER(),
                  "departs" : DBTYPES.INTEGER(),
                  "arrives" : DBTYPES.INTEGER(),
                  "lastname" : DBTYPES.TEXT(),
                  "firstname": DBTYPES.TEXT(),
                  "birthdate": DBTYPES.INTEGER(),
                  "gender": DBTYPES.TEXT(),
                  "ssn": DBTYPES.TEXT(),
                  "email" : DBTYPES.TEXT(),
                  "street": DBTYPES.TEXT(),
                  "zip" : DBTYPES.TEXT()}



ignore_fields = ["ssn", "uid", "zip", "serial", "lastname", "firstname", "email", "year", "birthyr", "age", "perwt", "gq", "pernum", "nchlt5", "relate", "related", "datanum", "yrnatur", "birthqtr", "marst", "marrno", "yrmarr", "race", "raced", "hispan", "hispand", "bpl", "bpld", "citizen", "racamind", "racasian", "racblk", "racpacis", "racwht", "racother", "yrimmig", "yrusa1", "language", "languaged", "hcovany", "hcovpriv", "hinsemp", "hinspur", "hinst, ri", "hcovpub", "hinscaid", "hinscare", "hinsva", "hinsihs", "school", "educd", "gradeattd", "degfieldd", "degfield2d", "empstatd", "labforce", "classwkrd", "wkswork2", "uhrswork", "absent", "looking", "availble", "wrkrecal", "workedyr", "ftotinc", "incwage", "incbus00", "incss", "incwelfr", "incinvst", "incretir", "incsupp", "incother", "incearn", "occscore", "migrate1", "migrate1d", "migplac1", "migpuma1", "movedin", "vetstat", "vetstatd", "vet01ltr", "pwstate2", "pwpuma00", "carpool", "riders", "tranwork", "departs", "arrives"]
position_fields = ["street"]
indexation = []
quid_cols = ["street", "birthdate", "occ", "ind", "inctot", "famsize", "nchild", "nsibs", "speakeng", "educ", "gradeatt", "schltype", "degfield", "degfield2", "empstat", "classwkr", "poverty"]
sensitive_cols = ["gender", "trantime", "vetdisab", "diffrem", "diffphys", "diffmob", "diffcare", "diffsens", "diffeye", "diffhear"]

def birthDateToAge(ligne):
    currentyear = datetime.datetime.now().year
    return currentyear - datetime.datetime.strptime(ligne["birthdate"], "%Y-%m-%d").year

raw_transform = {"birthdate" : birthDateToAge}


annonymizeGDATable("groupe_1_GDA", "", "census", "persons_temp_view", "raw_census", "persons_temp_view",
                   table_structure, ignore_fields, position_fields, indexation, quid_cols, sensitive_cols,4 , 1,
                   gda_raw_transform=raw_transform, use_cache=False)
