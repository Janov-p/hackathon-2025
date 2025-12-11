import csv

#Fonction de récupération des données classeur
def readRs(file_name:str, type:str):
  with open('eggs.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ')
    for row in spamreader:
      print(', '.join(row))
  return None

def readRsTest():
  with open('db/data/Corse Matin - RS_09122025.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ')
    for row in spamreader:
      print(', '.join(row))
  return None