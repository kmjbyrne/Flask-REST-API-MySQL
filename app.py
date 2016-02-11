from flask import Flask,render_template,jsonify,url_for,request,session,flash, json, Response
from urlparse import urlparse
import lib
import urllib2, json
from werkzeug import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from functools import wraps
import MySQLdb

# HTTP Request Detail
# TYPE : API Feature

# GET /table/list
# GET /table/structure (Deprecated from v1.x +)
# GET /table/showall
# POST /table/post
# GET /table/showone

app = Flask(__name__)

#######################
### CONFIG SETTINGS ###
#######################

host = 'localhost'
password = 'root'
user = 'root'
db = 'GamesDB'

content_type = 'application/vnd.collection+json'
api_root = '/api/'

cj = {}

def testItems():
	friends = []
	item={}
	item['name'] = 'mildred'
	item['email'] = 'mildred@example.com'
	item['blog'] = 'http://example.com/blogs/mildred'
	friends.append(item);

	item['name'] = 'mildred'
	item['email'] = 'mildred@example.com'
	item['blog'] = 'http://example.com/blogs/mildred'
	friends.append(item)

	item['name'] = 'mildred'
	item['email'] = 'mildred@example.com'
	item['blog'] = 'http://example.com/blogs/mildred'
	friends.append(item)

	item['name'] = 'mildred'
	item['email'] = 'mildred@example.com'
	item['blog'] = 'http://example.com/blogs/mildred'
	friends.append(item)

	item['name'] = 'mildred'
	item['email'] = 'mildred@example.com'
	item['blog'] = 'http://example.com/blogs/mildred'
	friends.append(item)

	return friends


def getCurrentPath(url, mod_path):
	parsed = urlparse(url)
	href = ''
	if(mod_path is None):
		href = ''.join(parsed.scheme, "://", parsed.netloc, parsed.path)
	else:
		href = ''.join([parsed.scheme, '://', parsed.netloc, mod_path])
	return href

def createSkeleton(url):
	pu = urlparse(url)
	base = pu.scheme + "://" + pu.netloc
	path = pu.path

	collection_json = {}
	collection_json['collection'] = {}
	collection_json['collection']['version'] = "1.0"
	collection_json['collection']['href'] = base + path
	collection_json['collection']['links'] = linksDefault(base + api_root)
	collection_json['collection']['items'] = []
	collection_json['collection']['queries'] = []
	collection_json['collection']['template'] = {}

	return collection_json


def linksDefault(path):
    links = []
    dict = {'rel': 'home', 'href': path}
    links.append(dict)
    return links

def runSQLQuery(_sql, code):
	"""Allow for variation in how SQL connection models INSERT's and SELECT's"""
	"""Divisioin of functionality simply using 0,1 code to decide route"""
	"""No need for commit on SELECT or UPDATE (code 2 -> later revision)"""
	con = MySQLdb.connect(host, user, password, db)
	cursor = con.cursor()

	if code == 0:
    	# All select queries here
		cursor.execute(_sql)
		data = cursor.fetchall()
		return data

	elif code == 1: 
    	#All insert queries here
		try:
			cursor.execute(_sql)
			con.commit()
			last_id = cursor.lastrowid
			return last_id 
		except Exception as e:
			print(str(e))
			return False

	cursor.close()
	con.close()

def generateError(title, code, message):
	item = {}
	item["title"]= title
	item["code"]= code
	item["message"]= message

	return item


def generateDynamicItem(columns, data):
	items = []
	counter = 0
	outer = 0

	for i in data:
		for x in i:
			dict = {'value': x[0]}
			items.append(dict)

	return jsonify(items)

def packageResponse(data):
	resp = jsonify(data)
	resp.status_code = 200
	resp.message ='OK'
	resp.content_type = content_type
	return resp


def generateTemplate():
	pass

@app.route('/', methods=['GET'])
def home():
	return render_template('index.html')

@app.route('/api/', methods=['GET'])
def root():
	url = request.url
	data = get_skeleton(url)
	data['collection']['items'] = testItems()
	return packageResponse(data)

@app.route('/api/table/list', methods=['GET', 'POST'])
def getTableList():

	url = request.url
	data = createSkeleton(url)

	query = "SHOW TABLES"
	query_results = runSQLQuery(query, 0)

	for i in query_results:
		item = {}
		table = i[0]
		mod_path = '/api/' + table
		item['href'] = getCurrentPath(url, mod_path)
		item['data'] = {'table': table}
		data['collection']['items'].append(item)

	return packageResponse(data)


@app.route('/api/<table>/', methods=['GET', 'POST'])
def tableRoute(table):
	url = request.url
	collection = createSkeleton(url)

	if(request.method == 'GET'):
		query = "DESCRIBE {0}".format(table)
		data = runSQLQuery(query, 0)

		for i in data:
			item={}
			item['field'] = i[0]
			item['type'] = i[1]
			item['nullable'] = i[2]
			item['key'] = i[3]
			item['default'] = str(i[4])
			item['extra'] = i[5]
			collection['collection']['items'].append(item)
		return packageResponse(collection)

	elif(request.method == 'POST'):
		try:
			data = json.dumps(request.get_json())
			dict_data = json.loads(data)
			query = ['INSERT ', 'INTO ', table, ' values ', '(null']

			uid = ''
			for item in dict_data['template']['data']:
				if(item['name'] == 'id'):
					uid = item['value']
				else:
					query.append(", '{0}'".format(item['value']))
					uid = uid + item['value']

			query.append(')')
			query = ''.join(query)

			uid = runSQLQuery(query, 1)
			if(uid != False):
				print("Insert successful")
				print(uid)
				collection['collection']['links'].append({'href': url + 'showall'})
				collection['collection']['links'].append({'href': url + 'showone/' + str(uid)})
				return packageResponse(collection)

			else:
				collection['error'] = generateError("Unable to insert item", "IE x0001", "Check data and try again")
				return packageResponse(collection)


		except Exception as e:
			collection['error'] = generateError("HTTP Error", "Unknown", str(e))
			return packageResponse(collection)


@app.route('/api/<table>/showone/<unique_href>', methods=['GET'])
def showone(table, unique_href):

	url = request.url
	collection = createSkeleton(url)
	column_query = "SHOW COLUMNS FROM {0}".format(table)
	columns = runSQLQuery(column_query, 0)

	query = "SELECT * FROM {0} WHERE {1} = {2}".format(table, columns[0][0], 1)
	
	rows = runSQLQuery(query, 0)
	item = {}
	data = []
	mod_path = '/api/table/showone/' + unique_href
	item['href'] = getCurrentPath(url, mod_path)
	#row_item={}
	row_item_data={}
	counter=0
	for x in columns:
		#temp['column']= str(x[0])
		#temp['value']= str(i[counter])
		row_item_data['{0}'.format(x[0])] = rows[0][counter]
		counter=counter+1

	item['links'] = []
	item['links'].append({'href': ''})
	item['links'].append({'href': ''})
	data.append(row_item_data)
	item['data'] = data
	collection['collection']['items'].append(item)
	
	return packageResponse(collection)

@app.route('/api/<table>/showall', methods=['GET'])
def showall(table):

	url = request.url
	collection = createSkeleton(url)

	query = "SELECT * FROM {0}".format(table)
	column_query = "SHOW COLUMNS FROM {0}".format(table)
	rows = runSQLQuery(query, 0)
	column_flags = runSQLQuery(column_query, 0)
	print(rows)
	print(column_flags)

	data = []
	for i in column_flags:
		item = {}
		item['name'] = i[0]
		item['value'] = ''
		data.append(item)
	
	collection['collection']['template'] = {'data': data}

	for i in rows:
		print(i)
		item = {}
		unique_ref = str(i[0]) + str(i[1])
		mod_path = '/api/table/showone/' + table + unique_ref
		item['href'] = getCurrentPath(url, mod_path)
		#row_item={}
		data = []
		row_item_data={}
		counter=0
		for x in column_flags:
			temp={}
			temp['column']= str(x[0])
			temp['value']= str(i[counter])
			#row_item_data['{0}'.format(x[0])] = i[counter]
			data.append(temp)
			
			counter=counter+1

		#data.append(row_item_data)
		item['data'] = data
		
		collection['collection']['items'].append(item)

	return packageResponse(collection)


if __name__ == '__main__':
    app.run(debug=True)