import os, sys
import yaml, dirutil
from cast import log
from cast import chaos


def csv(db, importfile):
    import csv
    with open(importfile, newline='') as csvfile:
        spam = csv.reader(csvfile, delimiter=';')
        header = spam[0]
        spam = [spam][1:]
        
        



    return dict()    