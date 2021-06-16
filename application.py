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
cando_obj = cnd.CANDO(cmpd_map, inds_map, matrix=matrix_file, compute_distance=True,
                  save_dists='test_rmsds.tsv', dist_metric='cosine', ncpus=1)
#cando_obj = cnd.load_version(v='v2.3', protlib='homo_sapien', i_score='CxP', approved_only=False, compute_distance=False
#, dist_metric='cosine', protein_set='', ncpus=1)

@app.route("/")
def home():
    return "home page"

@app.route("/cando")
def cando():
    return "cando page"

@app.route("/compounds_drugs")  
def compounds_drugs():
    return render_template('template.html', compounds_drugs_selection="current", cando_obj=cando_obj)

@app.route("/indications")
def indications():
    return render_template('template.html', indications_selection="current", cando_obj=cando_obj)

@app.route("/proteins")
def proteins():
    return "proteins page"

@app.route("/adr")
def adr():
    return "adr page"

@app.route("/canpredict_compounds", methods=['POST'])
def canpredict_compounds():
    body = dict(request.form)
    indication_id = body['indication']
    n = 10
    topX = 10
    consensus = False
    keep_associated = False
    cmpd_set = 'all'
    save = 'outputs/compounds_drugs/canpredict_compounds.txt'
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
    for key in body.keys():
        print(f"{key}: {body[key]}")
    cando_obj.canpredict_compounds(indication_id, n=n, topX=topX, consensus=consensus, keep_associated=keep_associated,
    cmpd_set=cmpd_set, save=save)
    return send_file(save, as_attachment=True)

if __name__ == "__main__":
    app.run()