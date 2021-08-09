from flask import Flask, redirect, render_template, request, flash, make_response, send_file
from flask_wtf import FlaskForm
import os
import cando as cnd

app = Flask(__name__)

matrix_file = 'cando/data/v2.2+/matrices/rd_ecfp4-nrpdb-v2.2-all-int_vect-dice-CxP.tsv'
cmpd_map = 'cando/data/v2.2+/mappings/drugbank-v2.2.tsv'
inds_map = 'cando/data/v2.2+/mappings/drugbank2ctd-v2.2.tsv'
file_name = "empty"
selected_method = ""
b = True
cando_obj = cnd.CANDO(cmpd_map, inds_map, matrix=matrix_file)

indication_mappings = {}
cmpd_mappings = {}
required_parameters = {"canpredict_compounds": ["ind_id"],
                       "canpredict_indications": ["cmpd"],
                       "canpredict_adr": ["cmpd"],
                       "canbenchmark": [],
                       "canbenchmark_associated": [],
                       "canbenchmark_ncdg": [],
                       "canbenchmark_cluster": [],
                       "canbenchmark_compounds": [],
                       "canbenchmark_ddi": []}
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
    return redirect("/cando")

@app.route("/cando")
def cando():
    global b
    global selected_method
    file = []
    if file_name != "empty" and b:
        with open(file_name) as f:
            for l in f:
                file.append(l.strip())
    b = False
    if not selected_method in cando_obj.cando_methods():
        selected_method = ""
    return render_template('cando.html', cando_selection="current", selected_method=selected_method, file=file, cando_obj=cando_obj, 
    cmpd_mappings=cmpd_mappings, indication_mappings=indication_mappings, required_parameters=required_parameters)

@app.route("/compounds_drugs")
def compounds_drugs():
    global b
    global selected_method
    file = []
    if file_name != "empty" and b:
        with open(file_name) as f:
            for l in f:
                file.append(l.strip())
    b = False
    if not selected_method in cando_obj.compounds_drugs_methods():
        selected_method = ""
    return render_template('cando.html', compounds_drugs_selection="current", selected_method=selected_method, file=file, cando_obj=cando_obj, 
    cmpd_mappings=cmpd_mappings, indication_mappings=indication_mappings, required_parameters=required_parameters)
    
@app.route("/indications")
def indications():
    global b
    global selected_method
    file = []
    if file_name != "empty" and b:
        with open(file_name) as f:
            for l in f:
                file.append(l.strip())
    b = False
    if not selected_method in cando_obj.indications_methods():
        selected_method = ""
    return render_template('cando.html', indications_selection="current", selected_method=selected_method, file=file, cando_obj=cando_obj, 
    cmpd_mappings=cmpd_mappings, indication_mappings=indication_mappings, required_parameters=required_parameters)

@app.route("/adr")
def adrs():
    global b
    global selected_method
    file = []
    if file_name != "empty" and b:
        with open(file_name) as f:
            for l in f:
                file.append(l.strip())
    b = False
    if not selected_method in cando_obj.adr_methods():
        selected_method = ""
    return render_template('cando.html', adr_selection="current", selected_method=selected_method, file=file, cando_obj=cando_obj, 
    cmpd_mappings=cmpd_mappings, indication_mappings=indication_mappings, required_parameters=required_parameters)

@app.route("/canpredict_compounds", methods=['POST'])
def canpredict_compounds():
    global file_name
    global b
    body = dict(request.form)
    indication_id = body['indication'].strip()
    if indication_id.strip()[0:4] != "MESH":
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
    return redirect("/compounds_drugs")

@app.route("/canpredict_indications", methods=['POST'])
def canpredict_indications():
    global file_name
    global b
    body = dict(request.form)
    cmpd_id = int(body['cmpd'].strip())
    n = 10
    topX = 10
    save="outputs/indications/canpredict_indications.txt"
    if 'n' in body.keys() and len(body['n']) > 0:
        n = int(body['n'])
    if 'topX' in body.keys() and len(body['topX']) > 0:
        topX = int(body['topX'])
    cmpd = cando_obj.get_compound(cmpd_id)
    cando_obj.canpredict_indications(cmpd, n=n, topX=topX, save=save)
    file_name = save
    b = True
    return redirect("/indications")

@app.route("/canpredict_adr", methods=['POST'])
def canpredict_adr():
    global file_name
    global b
    body = dict(request.form)
    cmpd_id = int(body['cmpd'].strip())
    n = 10
    topX = 10
    save="outputs/indications/canpredict_adr.txt"
    if 'n' in body.keys() and len(body['n']) > 0:
        n = int(body['n'])
    if 'topX' in body.keys() and len(body['topX']) > 0:
        topX = int(body['topX'])
    cmpd = cando_obj.get_compound(cmpd_id)
    cando_obj.canpredict_adr(cmpd, n=n, topX=topX, save=save)
    file_name = save
    b = True
    return redirect("/adrs")

@app.route("/canbenchmark", methods=['POST'])
def canbenchmark():
    global file_name
    global b
    body = dict(request.form)
    file_name = "basic"
    indications = []
    continuous = False
    bottom = False
    ranking = "standard"
    adrs = False
    if 'file_name' in body.keys() and len(body['file_name']) > 0:
        file_name = body['file_name'].strip()
    if 'indications' in body.keys() and len(body['indication']) > 0:
        indications = body['indication'].strip().split(",")
    if 'continuous' in body.keys() and body['continuous'] != None:
        if body['continuous'].strip() == 'True':
            continuous = True
        else:
            continuous = False
    if 'bottom' in body.keys() and body['bottom'] != None:
        if body['bottom'].strip() == 'True':
            bottom = True
        else:
            bottom = False
    if 'ranking' in body.keys() and len(body['ranking']) > 0:
        ranking = body['ranking'].strip().lower()
    if 'adrs' in body.keys() and body['adrs'] != None:
        if body['adrs'].strip() == 'True':
            adrs = True
        else:
            adrs = False
    
    cando_obj.canbenchmark(file_name=file_name, indications=indications, continuous=continuous, bottom=bottom, ranking=ranking, adrs=adrs)
    file_name = "results_analysed_named/results_analysed_named-"+file_name+".tsv"
    b=True
    return redirect("/indications")

@app.route("/canbenchmark_associated", methods=['POST'])
def canbenchmark_associated():
    global file_name
    global b
    body = dict(request.form)
    file_name = "associated"
    indications = []
    continuous = False
    ranking = "standard"
    if 'file_name' in body.keys() and len(body['file_name']) > 0:
        file_name = body['file_name'].strip()
    if 'indications' in body.keys() and len(body['indication']) > 0:
        indications = body['indication'].strip().split(",")
    if 'continuous' in body.keys() and body['continuous'] != None:
        if body['continuous'].strip() == 'True':
            continuous = True
        else:
            continuous = False
    if 'ranking' in body.keys() and len(body['ranking']) > 0:
        ranking = body['ranking'].strip().lower()
    cando_obj.canbenchmark_associated(file_name=file_name, indications=indications, continuous=continuous, ranking=ranking)
    file_name = "results_analysed_named/results_analysed_named-"+file_name+".tsv"
    b=True
    return redirect("/indications")

@app.route("/canbenchmark_bottom", methods=['POST'])
def canbenchmark_bottom():
    global file_name
    global b
    body = dict(request.form)
    file_name = "bottom"
    indications = []
    ranking = "standard"
    if 'file_name' in body.keys() and len(body['file_name']) > 0:
        file_name = body['file_name'].strip()
    if 'indications' in body.keys() and len(body['indication']) > 0:
        indications = body['indication'].strip().split(",")
    if 'ranking' in body.keys() and len(body['ranking']) > 0:
        ranking = body['ranking'].strip().lower()
    cando_obj.canbenchmark_bottom(file_name=file_name, indications=indications, ranking=ranking)
    file_name = "results_analysed_named/results_analysed_named-"+file_name+".tsv"
    b=True
    return redirect("/indications")

@app.route("/canbenchmark_cluster", methods=['POST'])
def canbenchmark_cluster():
    global file_name
    global b
    body = dict(request.form)
    file_name = "cluster"
    n_clusters = 5
    if 'n_clusters' in body.keys() and len(body['n_clusters']) > 0:
        n_clusters = int(body['n_clusters'].strip())
    cando_obj.canbenchmark_cluster(n_clusters=n_clusters)
    file_name = "results_analysed_named/results_analysed_named-"+file_name+".tsv"
    b=True
    return redirect("/indications")

@app.route("/canbenchmark_compounds", methods=['POST'])
def canbenchmark_compounds():
    global file_name
    global b
    body = dict(request.form)
    file_name = "compounds"
    adrs = []
    continuous = False
    bottom = False
    ranking = "standard"
    if 'file_name' in body.keys() and len(body['file_name']) > 0:
        file_name = body['file_name'].strip()
    if 'adrs' in body.keys() and len(body['adrs']) > 0:
        adrs = body['adrs'].strip().split(",")
    if 'continuous' in body.keys() and body['continuous'] != None:
        if body['continuous'].strip() == 'True':
            continuous = True
        else:
            continuous = False
    if 'bottom' in body.keys() and body['bottom'] != None:
        if body['bottom'].strip() == 'True':
            bottom = True
        else:
            bottom = False
    if 'ranking' in body.keys() and len(body['ranking']) > 0:
        ranking = body['ranking'].strip().lower()
    cando_obj.canbenchmark_compounds(file_name=file_name, adrs=adrs, continuous=continuous, bottom=bottom, ranking=ranking)
    file_name = "results_analysed_named/results_analysed_named-"+file_name+".tsv"
    b=True
    return redirect("/indications")

@app.route("/canbenchmark_ddi", methods=['POST'])
def canbenchmark_ddi():
    global file_name
    global b
    body = dict(request.form)
    file_name = "ddi"
    adrs = []
    continuous = False
    bottom = False
    ranking = "standard"
    if 'file_name' in body.keys() and len(body['file_name']) > 0:
        file_name = body['file_name'].strip()
    if 'adrs' in body.keys() and len(body['adrs']) > 0:
        adrs = body['adrs'].strip().split(",")
    if 'continuous' in body.keys() and body['continuous'] != None:
        if body['continuous'].strip() == 'True':
            continuous = True
        else:
            continuous = False
    if 'bottom' in body.keys() and body['bottom'] != None:
        if body['bottom'].strip() == 'True':
            bottom = True
        else:
            bottom = False
    if 'ranking' in body.keys() and len(body['ranking']) > 0:
        ranking = body['ranking'].strip().lower()
    cando_obj.canbenchmark_ddi(file_name=file_name, adrs=adrs, continuous=continuous, bottom=bottom, ranking=ranking)
    file_name = "results_analysed_named/results_analysed_named-"+file_name+".tsv"
    b=True
    return redirect("/indications")

@app.route("/canbenchmark_ndcg", methods=['POST'])
def canbenchmark_ndcg():
    global file_name
    global b
    body = dict(request.form)
    file_name = "ndcg"
    cando_obj.canbenchmark_ndcg(file_name=file_name)
    file_name = "results_analysed_named/results_analysed_named_ndcg-"+file_name+".tsv"
    b=True
    return redirect("/indications")

@app.route('/form_selection', methods=['POST'])
def form_selection():
    global selected_method
    body = dict(request.form)
    selected_method = body['selection'].strip()
    return redirect("/"+body['reroute'])

@app.route('/download')
def download():
    return send_file(file_name, as_attachment=True)

if __name__ == "__main__":
    app.run()