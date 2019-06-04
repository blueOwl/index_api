from retrieve import Retrieve
from flask import Flask, jsonify, abort, session, request, send_from_directory
from utils import PageHolder, index_get_func
from parse_description_file import get_anno_tree_dic
from flask_cors import CORS
from hash_idx import H_idx
from db import *
import config
import uuid

PH = PageHolder()
app = Flask(__name__)
CORS(app)
#init retrieve motheds
dbs = {}
for k in ['HRC']:
	dbs[k] = Retrieve(k)
full_headers = dbs[k].get_header_list()
single_page_info = {"page_num":1,
                 "total_page":1,
                 "page_size":1}
#idx_db = H_idx("HRC")
#idx_db = {}

#get /header/<dataset>
@app.route('/header/<string:dataset>')
def get_header(dataset):
	if not dataset in dbs:
		abort(404)
	if request.args.get('chrom'):
		chrom = request.args.get('chrom')
	else:
		chrom = ''
	headers = dbs[dataset].get_headers()
	return jsonify(headers)	

#get /download/<folder>/<name>
@app.route('/download/<folder>/<name>', methods=['GET'])
def download_file(folder, name):
	if not folder in config.DOWNLOAD_DIR: 
		abort(400)
	return send_from_directory(folder, name, as_attachment=True)

#get /origin/<dataset>
@app.route('/origin/<string:dataset>')
def get_origin(dataset):
	if not dataset in dbs:
		abort(404)
	link_list = [ "/download/" + 'data/' + name for name in dbs[dataset].get_data_file_names()]
	res = {'data':link_list,
                'format': 'links'}
	return jsonify(res)

#get /region/<dataset>
@app.route('/region/<string:dataset>')
def get_region(dataset):
	if not dataset in dbs:
		abort(404)
	chrom, start, end = request.args.get('chrom'), request.args.get('start'), request.args.get('end')

	try:
		idx = request.args.get('headers')
		if idx:
			idx = [int(i) for i in idx.split(' ')]
			col_filter = index_get_func(idx)
		else:
			col_filter = list
	except:
		col_filter = list
	if not chrom : abort(400)
	try:
		start, end = int(start), int(end)
	except:
		abort(400)

	#prepare result
	query_result = dbs[dataset].region_query(chrom, start, end, col_filter)
	page = query_result.get_cur_page()
	pid = ''
	if query_result.has_next():
		pid = PH.put(query_result)
		next_page = config.HOST + "/nextpage/" + pid
	else:
		next_page =  'None'
	#header = dbs[dataset].get_header_list()
	header = query_result.headers
	res = { 'format': 'json', 
		'data':page,
		'next_page': next_page,
		'page_info': query_result.get_page_info(),
		'page_id':pid,
		'headers': header}
	return jsonify(res)
#get /gene/<dataset>
@app.route('/gene/<string:dataset>')
def get_gene(dataset):
	if not dataset in dbs:
		print('dataset not found')
		abort(404)
	gene_name = request.args.get('gene')
	gene = find_gene(gene_name)
	#print(gene)
	if gene: 
		chrom, start, end = gene
		if end < start: start, end = end, start
	else:
		print('no gene')
		abort(404)
	try:
		idx = request.args.get('headers')
		if idx:
			idx = [int(i) for i in idx.split(' ')]
			print("gene query with headers", idx)
			col_filter = index_get_func(idx)
		else:
			col_filter = list
	except:
		col_filter = list
	if not chrom : 
		print('chrom not found')
		abort(400)
	try:
		start, end = int(start), int(end)
	except:
		print('gene info wrong')
		abort(400)

	#prepare result
	query_result = dbs[dataset].region_query(chrom, start, end, col_filter)
	page = query_result.get_cur_page()
	pid = ''
	if query_result.has_next():
		pid = PH.put(query_result)
		next_page = config.HOST + "/nextpage/" + pid
	else:
		next_page =  'None'
	#header = dbs[dataset].get_header_list()
	header = query_result.headers
	res = { 'format': 'json', 
		'gene_info':{
			'uniprot_id':gene_name,
			'contig': chrom,
			'start':start,
			'end':end
		},
		'data':page,
		'next_page': next_page,
		'page_info': query_result.get_page_info(),
		'page_id':pid,
		'headers': header}
	return jsonify(res)

@app.route('/gotopage/<string:pid>/<int:pnum>')
def get_page(pid, pnum):
	query_result = PH.get(pid)
	if not query_result: abort(404)
	page = query_result.get_page(pnum)
	if not page: abort(404)
	if query_result.has_next():
		next_page = config.HOST + "/nextpage/" + pid
	else:
		next_page =  'None'
	header = query_result.headers
	res = { 'format': 'json', 
		'data':page,
		'page_info': query_result.get_page_info(),
		'page_id':pid,
		'headers':header,
		'next_page': next_page}
	return jsonify(res)

@app.route('/total_res/<string:pid>')
def get_download_url(pid):
	query_result = PH.get(pid)
	if not query_result: abort(404)
	filename = query_result.filename
	if not filename:
		filename = query_result.write_to_file(config.TMPDIR[query_result.info.get('dataset')])
	res = {"url": "/download/" + 'tmp/' + filename}
	return jsonify(res)

@app.route('/nextpage/<string:pid>')
def get_nextpage(pid):
	query_result = PH.get(pid)
	if not query_result: abort(404)
	page = query_result.get_cur_page()
	if not page: abort(404)
	if query_result.has_next():
		next_page = config.HOST + "/nextpage/" + pid
	else:
		next_page =  'None'
		del PH[pid]
	header = query_result.headers
	res = { 'format': 'json', 
		'data':page,
		'page_info': query_result.get_page_info(),
		'page_id':pid,
		'headers':header,
		'next_page': next_page}
	return jsonify(res)

@app.route('/rs/<string:rsid>')
def get_rs(rsid):
	res = key_get(rsid, list)
	return jsonify({'data':[res], 
			'page_info':single_page_info,
			'page_id':'',
			"headers":full_headers})

@app.route('/variant/<string:vid>')
def get_variant(vid):
	res = key_get(vid, list)
	return jsonify({'data':[res],
			'page_id':'',
			'page_info':single_page_info,
			"headers":full_headers})


@app.route('/anno_tree/<string:dataset>')
def get_anno_tree(dataset):
	if not dataset in dbs:
		abort(404)
	tree_dic = get_anno_tree_dic(dataset)
	for idx in config.DEFAULT_IDXS: 
		if idx in tree_dic:
			del tree_dic[idx]
	return jsonify({"header_tree_array":[tree_dic[i].get_dic() for i in sorted(tree_dic.keys())]})

@app.route('/vcf', methods=['POST'])
def vcf_intersect():
	idx = []#request.values.get('headers')
	vcf_file = request.files.get('vcf')
	#print([i for i in request.values])
	#print([i for i in request.files])
	#print([i for i in request.args])
	#print(request.get_json())
	#try:
	if not vcf_file:
		req_json = request.get_json()
		print([i for i in req_json['params']])
		print("H", req_json['params']['headers'])
		idx = [int(i) for i in req_json['params']['headers'].split(' ') if not i == ' ']
		vcf_file = [i.encode('utf8') for i in req_json['params']['uploadList']['ids'].split('\n')]
	if not vcf_file: abort(404)
	if idx:
		idx = sorted(list(set([int(i) for i in idx])))
		print(idx)
		col_filter = index_get_func(idx)
	else:
		col_filter = list
	
	res = intersect_vcf(vcf_file, col_filter)
	filename =  str(uuid.uuid4())
	f = open(config.TMPDIR["HRC"] + filename, 'w')
	f.write("\t".join(col_filter(full_headers)) + "\n")
	for i in res:
		f.write('\t'.join(i) + "\n")
	
	return jsonify({"url": "/download/" + 'tmp/' + filename})



app.run(host="0.0.0.0", port=5000)
