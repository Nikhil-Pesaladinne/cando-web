from flask import Flask, redirect, render_template, request, flash, make_response, send_file
from flask_wtf import FlaskForm
import os
import cando as cnd

app = Flask(__name__)

matrix_file = 'cando/data/v2.2+/test/test-matrix.tsv'
inds_map = 'cando/data/v2.2+/test/test-inds.tsv'
cmpd_map = 'cando/data/v2.2+/test/test-cmpds.tsv'
cmpd_dir = 'cando/data/v2.2+/test/test-cmpds_mol/'
new_cmpds = 'cando/data/v2.2+/test/test-new_cmpds.tsv'
file_name = "empty"
b = True
cando_obj = cnd.CANDO(cmpd_map, inds_map, matrix=matrix_file, compute_distance=True,
                  save_dists='test_rmsds.tsv', dist_metric='cosine', ncpus=1)

indication_mappings = {}
cmpd_mappings = {}
with open(inds_map) as f:
    for l in f:
        line = l.strip().split('\t')
        indication_mappings[line[1]] = (line[0],line[2], line[3])
with open(cmpd_map) as f:
    for l in f:
        line = l.strip().split('\t')
        cmpd_mappings[line[2]] = line[1]
        
#cando_obj = cnd.load_version(v='v2.3', protlib='homo_sapien', i_score='CxP', approved_only=False, compute_distance=False
#, dist_metric='cosine', protein_set='', ncpus=1)

@app.route("/")
def home():
    return "HOME PAGE"

@app.route("/cando")
def cando():
    global b
    file = []
    if file_name != "empty" and b:
        with open(file_name) as f:
            for l in f:
                file.append(l.strip())
    b = False
    return render_template('cando.html', cando_selection="current", file=file, file_name=file_name, cando_obj=cando_obj, cmpd_mappings=cmpd_mappings, indication_mappings=indication_mappings)

@app.route("/compounds_drugs")
def compounds_drugs():
    return "Compounds page"
    
@app.route("/canpredict_compounds", methods=['POST'])
def canpredict_compounds():
    global file_name
    global b
    body = dict(request.form)
    indication_id = indication_mappings[body['indication'].strip()][1]
    n = 10
    topX = 10
    consensus = False
    keep_associated = False
    cmpd_set = 'all'
    save="outputs/compounds_drugs/canpredict_compounds.txt"
    if 'n' in body.keys() and len(body['n']) > 0:
        n = int(body['n'])
    if 'topX' in body.keys() and len(body['topX']) > 0:
        topX = int(body['topX'])
    if 'consensus' in body.keys() and body['consensus'] != None:
        if body['consensus'] == 'True':
            consensus = True
        else:
            consensus = False
    if 'keep_associated' in body.keys() and body['keep_associated'] != None:
        if body['keep_associated'] == 'True':
            keep_associated = True
        else:   
            keep_associated = False
    cando_obj.canpredict_compounds(indication_id, n=n, topX=topX, consensus=consensus, keep_associated=keep_associated,
    cmpd_set=cmpd_set, save=save)
    file_name = save
    b = True
    return redirect("/cando")

@app.route('/download')
def download():
    return send_file(file_name, as_attachment=True)

if __name__ == "__main__":
    app.run()