from mod.lib.text import normalize
from mod.root.data import db

def __classify(db, vy, w):
    w = normalize(w)
    db.exec("UPDATE words SET vy = ? WHERE vy = '' AND word LIKE ?", vy, w)
    
def classify():
    db.begin()

    # db.exec("UPDATE words SET vy = ''")
    __classify(db, 'A/tum', '%tuṁ')
    __classify(db, 'A/tum', '%tum')
    __classify(db, 'A/tva', '%tvā')

    __classify(db, 'P1.1/lrt', '%āsyati')
    __classify(db, 'P1.1/lrt', '%iṣyati')
    # __classify(db, 'P1.2/lrt' WHERE word LIKE '%iṣyataḥ'")
    __classify(db, 'P1.3/lrt', '%iṣyanti')
    __classify(db, 'P2.1/lrt', '%iṣyasi')
    __classify(db, 'P2.2/lrt', '%iṣyathaḥ')
    __classify(db, 'P2.3/lrt', '%iṣyatha')
    __classify(db, 'P3.1/lrt', '%iṣyāmi')
    __classify(db, 'P3.2/lrt', '%iṣyāvaḥ')
    __classify(db, 'P3.3/lrt', '%iṣyāmaḥ')

    __classify(db, 'P1.1/lat', '%ati')
    # __classify(db, 'P1.1/lat', '%ataḥ')
    __classify(db, 'P1.3/lat', '%anti')
    __classify(db, 'P2.1/lat', '%asi')
    __classify(db, 'P2.2/lat', '%athaḥ')
    __classify(db, 'P2.3/lat', '%atha')
    __classify(db, 'P3.1/lat', '%āmi')
    __classify(db, 'P3.2/lat', '%āvaḥ')
    __classify(db, 'P3.3/lat', '%āmaḥ')

    __classify(db, 'V3.2 V4.2 V5.2', '%bhyāṁ')
    __classify(db, 'V3.2 V4.2 V5.2', '%bhyām')
    __classify(db, 'V3.3', '%bhiḥ')
    __classify(db, 'V4.3 V5.3', '%bhyaḥ')

    __classify(db, 'V6.1', '%asya') # ??

    __classify(db, 'V6.2 V7.2', '%yōḥ')

    __classify(db, 'V6.3', '%nām') # ?? kalpanAm
    __classify(db, 'V6.3', '%nāṁ')
    __classify(db, 'V6.3', '%ṇām')
    __classify(db, 'V6.3', '%ṇāṁ')

    __classify(db, 'V7.3', '%su')
    __classify(db, 'V7.3', '%ṣu')

    __classify(db, 'V1.1', '%vān')
    __classify(db, 'V1.1', '%vatī')

    __classify(db, 'V3.1', '%ēna')
    __classify(db, 'V3.1', '%ēṇa')

    __classify(db, 'V5.1 V6.1', '%āyāḥ')
    __classify(db, 'V7.1', '%āyāṁ')
    __classify(db, 'V7.1', '%āyām')

    __classify(db, 'V1.3 V2.3', '%āni')
    __classify(db, 'V1.3 V2.3', '%āṇi')

    db.commit()
