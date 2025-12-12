import jsonLoader as js
import extractMeasure as em
import prevision as pv
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__ ),'..', 'calculate')))

dt = js.simplification("db/VF_OneNext.json","femme")
#print(js.simplification("db/VF_OneNext.json","femme"))

print(em.extractDataOneNext(dt,"ensemble","penetration"))

print(pv.modelAR1)