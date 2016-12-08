import sqlite3
zotero = sqlite3.connect('database/zotero.sqlite')
zoteroCursor = zotero.cursor()

# get fields name & ID
Fields = zoteroCursor.execute("""SELECT * FROM fields""").fetchall()
FieldsDict = {x[0]:x[1] for x in Fields}

# get itemData name & ID
itemData = zoteroCursor.execute("""SELECT * FROM itemData""").fetchall()

# get itemData name & ID
itemDataValues = zoteroCursor.execute("""SELECT * FROM itemDataValues""").fetchall()
itemDataValuesDict = {x[0]: x[1] for x in itemDataValues}

fields = ["url", "DOI", "abstractNote", "title"]
fieldIDs = [1, 26, 90, 110]
items = {}

for iD in itemData:
    if iD[1] in fieldIDs: # is a field we want
        try:
            items[iD[0]][FieldsDict[iD[1]]] = itemDataValuesDict[iD[2]]
        except KeyError:
            items[iD[0]] = {FieldsDict[iD[1]]: itemDataValuesDict[iD[2]]}


import re
pattern = re.compile('[\W_]+')

for k, v in items.iteritems():
    try:
        strings = v["title"] + " " + v["abstractNote"]
    except KeyError:
        try:
            strings = v["title"]
        except KeyError:
            try:
                strings = v["abstractNote"]
            except KeyError:
                items[k]['strings'] = ""
                continue
    items[k]['strings'] = pattern.sub('', strings).lower()

def searchKeywords(key1, key2):
    i = []
    key1 = pattern.sub('', key1).lower()
    key2 = pattern.sub('', key2).lower()
    for k, v in items.iteritems():
        if (key1 in v['strings']) and (key2 in v['strings']):
            i.append(k)
    return i

keywords = ['first order', 'surface', 'melting', 'hard sphere', 'colloid',
            'dynamics', 'glass', 'nonequilibrium', 'statistical mechanics', 'DFT',
            'phase field', 'renormalization', 'review', 'shear']

results = {}
results["nodes"] = []
links = []
for i1 in range(len(keywords)):
    key1 = keywords[i1]
    x = searchKeywords(key1, "")
    results["nodes"].append({"name": key1, "r": len(x), "infolist": x})
    for i2 in range(i1):
        key2 = keywords[i2]
        x = searchKeywords(key1, key2)
        if len(x) > 0 :
            links.append({"source": i1, "target": i2, "name": key1+' + '+key2,
                          "weight": len(x),
                          "infolist": x})
results["links"] = links
results["items"] = items

import json
with open('network.json', 'w') as fp:
    json.dump(results, fp)
