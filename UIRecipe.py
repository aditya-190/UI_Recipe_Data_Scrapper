import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json

credential = credentials.Certificate('private.json')
firebase_admin.initialize_app(credential)
db = firestore.client()
with open("xd.json", "r") as read_file:
    data1 = json.load(read_file)
    doc_ref1 = db.collection("xd")

    xdCounter = 0
    for datum1 in data1:
        doc_ref1.add(datum1)
        xdCounter = xdCounter + 1
        print("XD -> " + str(xdCounter))

print("---------XD Completes Here---------")

with open("sketch.json", "r") as read_file:
    data2 = json.load(read_file)
    doc_ref2 = db.collection("sketch")
    sketchCounter = 0
    for datum2 in data2:
        doc_ref2.add(datum2)
        sketchCounter = sketchCounter + 1
        print("SKETCH -> " + str(sketchCounter))

print("---------SKETCH Completes Here---------")

with open("figma.json", "r") as read_file:
    data3 = json.load(read_file)
    doc_ref3 = db.collection("figma")
    figmaCounter = 0
    for datum3 in data3:
        doc_ref3.add(datum3)
        figmaCounter = figmaCounter + 1
        print("FIGMA -> " + str(figmaCounter))

print("---------FIGMA Completes Here---------")
