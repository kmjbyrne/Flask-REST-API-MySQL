from flask import Flask,render_template,jsonify,url_for,request,session,flash, json, Response
from urlparse import urlparse
import lib
import urllib2, json
from werkzeug import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from functools import wraps
import MySQLdb
from lib.collection import Structure

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
password = 'gamesadminpasswd'
user = 'gamesadmin'
db = 'GamesDB'

content_type = 'application/vnd.collection+json'
api_root = '/table'

cj = {}

###############################################
##### 	Standard functions & Test Data ########
###############################################

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

def describeAPI(url):
	collection = createSkeleton(url)
	collection['collection']['links'].append(generateLink(getCurrentPath(url, '/table/list'), 'list tables'))
	collection['collection']['links'].append(generateLink(getCurrentPath(url, '/table/<table>'), '[GET] describe table'))
	collection['collection']['links'].append(generateLink(getCurrentPath(url, '/table/showall/<table>'), 'show all from table'))
	collection['collection']['links'].append(generateLink(getCurrentPath(url, '/table/showone/<table>/<unique_href>'), 'show one from table'))
	collection['collection']['links'].append(generateLink(getCurrentPath(url, '/table/<table>'), '[POST] post to table'))
	return collection

def generateLink(link, rel):
	link_item = {}
	link_item['href'] = link
	link_item['rel'] = rel
	return link_item

def getCurrentPath(url, mod_path):
	parsed = urlparse(url)
	href = ''
	if(mod_path is None):
		href = ''.join(parsed.scheme, "://", parsed.netloc, parsed.path)
	else:
		href = ''.join([parsed.scheme, '://', parsed.netloc, mod_path])
	return href

def linksDefault(path):
    links = []
    dict = {'rel': 'home', 'href': path + "/list"}
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
	elif code == 2:
		#All special describe queries here
		try:
			cursor.execute(_sql)
			con.commit()
			return cursor
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
	resp = jsonify(data.getCollection())
	resp.status_code = 200
	resp.message ='OK'
	resp.content_type = content_type
	return resp

def generateTemplate(table_name):
	#Essentially describing table
	#Returning column types and 
	#Column names for INSERT reference
	template = {}
	data = []
	tables = [table_name]
	description = describeOne(table_name)
	print(description)
	for i in description:
		if(i[0] == 'id'):
			pass
		else:
			item = {}
			item['prompt'] = "type " + i[1]
			item['name'] = i[0]
			item['value'] = ""
			data.append(item)
			print(i)
	template['data'] = data

	return template

def getTables():
	query = "SHOW TABLES"
	tables = runSQLQuery(query, 0)
	return tables

def describeOne(table):
	query = "DESCRIBE {0}".format(table)
 	return runSQLQuery(query, 0)
	
def describeTables(url, list_of_tables):

	items = []
  	data = []
  	print(list_of_tables)
	for x in list_of_tables:
		query = "DESCRIBE {0}".format(x)
 		cursor = runSQLQuery(query, 2)
		headers = cursor.description

		print(headers)
		item = {}
		item['href'] = url
		item['data'] = []

		table_data = cursor.fetchall()
		
		for i in table_data:	
			counter = 0
			inner_data = []
			for col in i:
				print(col)
				data_item = {}
				data_item['name'] = headers[counter][0]
				data_item['value'] = col
				counter = counter + 1
				inner_data.append(data_item)

		item['data'] = inner_data
		items.append(item)
	return items


def generateNameValuePair(name, value):
	item = {}
	item['name'] = name
	item['value'] = value
	return item

###########################################################################################
###########################################################################################
###########################################################################################
##### Python API Section 															#######
##### GET /table/list [Show's all tables in DB]										#######
##### GET /table/<table> 					[HTTP Parameter Value]					#######	
##### GET /table/showall/<table> 			[HTTP Parameter Value]					#######	
##### POST /table/<table>					[HTTP Parameter Value]					#######	
##### GET /table/showone/<table>/<uid> 		[HTTP Parameter  Table & Unique HREF]	#######
##### GET /db/list 																	#######	
###########################################################################################
###########################################################################################
###########################################################################################

"""API ROOT - Describes API links in return object """
@app.route('/', methods=['GET'])
def root():
	url = request.url
	data = Structure(url)
	print(data)
	return packageResponse(data)

"""Original spec - deprecated as of v2.0 on request"""
@app.route('/db/list')
def showDatabases():
	url = request.url
	collection = Structure(url)
	query = "SHOW DATABASES"
	data = runSQLQuery(query, 0)
	for x in data:
		collection.appendItem(generateNameValuePair('database', x[0]))

	return packageResponse(collection)

@app.route('/table/list', methods=['GET', 'POST'])
def getTableList():

	url = request.url
	collection = Structure(url)
	query_results = getTables()

	for i in query_results:
		item = {}
		mod_path = '/table/' + i[0]
		item['href'] = getCurrentPath(url, mod_path)
		item['data'] = []
		item['data'].append(generateNameValuePair('table', i[0]))
		collection.appendItem(item)

	return packageResponse(collection)

@app.route('/table/<table>', methods=['GET', 'POST'])
def tableRoute(table):
	url = request.url
	collection = Structure(url)

	if(request.method == 'GET'):
		dbs = [table]	
		print(describeTables(url, dbs))
		collection.setItems(describeTables(url, dbs))
		link = getCurrentPath(url, '/table/' + table)

		collection.appendLink(generateLink(link, 'post'))
		return packageResponse(collection)

	elif(request.method == 'POST'):
		try:
			dict_data = None
			try:
				data = json.dumps(request.get_json())
				dict_data = json.loads(data)
				if(dict_data == None):
					raise Exception('Exception raised - JSON data package is None')

			except Exception as e:
				collection.setError(generateError("NO DATA", "IE x0001", str(e)))
				collection.setPostTemplate(generateTemplate(table))
				return packageResponse(collection)

			query = ['INSERT ', 'INTO ', table, ' values ', '(']

			uid = ''

			for item in dict_data['template']['data']:
				print('YES')
				if(item['name'] == 'id'):
					uid = item['value']
				else:
					query.append(", '{0}'".format(item['value']))
					uid = uid + item['value']

			query.append(')')
			query = ''.join(query)
			status = runSQLQuery(query, 1)

			if(status != False):
				print("Insert successful")
				print(status)
				link = getCurrentPath(url, "/table/showall/" + table)
				collection.appendLink(generateLink(link, 'showall'))
				link = getCurrentPath(url, "/table/showone/" + str(status))
				collection.appendLink(generateLink(link, 'showone'))
				return packageResponse(collection)

			else:
				collectionsetError(generateError("Unable to insert item", "IE x0002", "Check data and try again"))
				return packageResponse(collection)


		except Exception as e:
			collection.setError(generateError("HTTP Error", "Unknown", str(e)))
			collection.setPostTemplate(generateTemplate(table))
			return packageResponse(collection)

@app.route('/table/showone/<table>/<id>', methods=['GET'])
def showone(table, id):
	url = request.url
	collection = Structure(url)
	column_query = "SHOW COLUMNS FROM {0}".format(table)
	columns = runSQLQuery(column_query, 0)

	query = "SELECT * FROM {0} WHERE {1} = {2}".format(table, columns[0][0], id)
	
	rows = runSQLQuery(query, 0)
	item = {}
	data = []
	mod_path = '/table/showone/' + id
	item['href'] = getCurrentPath(url, mod_path)
	#row_item={}
	row_item_data = []
	counter=0

	if len(rows) == 0:
		collection.setError(generateError("Does not exist", "IE x0003", "Item HREF does not correspond to any data"))
	else:
		for x in columns:
			data_item = {}
			data_item['name'] = x[0]
			data_item['value'] = rows[0][counter]
			row_item_data.append(data_item)
			#temp['column']= str(x[0])
			#temp['value']= str(i[counter])
			counter=counter+1

		link = getCurrentPath(url, mod_path)
		collection.appendLink(generateLink(link, 'showone'))
		link = getCurrentPath(url, '/table/showall')
		collection.appendLink(generateLink(link, 'showall'))
		link = getCurrentPath(url, '/table/' + table)
		collection.appendLink(generateLink(link, 'post'))

		item['data'] = row_item_data
		collection.appendItem(item)

	collection.setPostTemplate(generateTemplate(table))
	
	return packageResponse(collection)

@app.route('/table/showall/<table>', methods=['GET'])
def showall(table):

	url = request.url
	collection = Structure(url)

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
	
	collection.setPostTemplate(generateTemplate(table))

	for i in rows:
		print(i)
		item = {}
		unique_ref = str(i[0])
		mod_path = '/table/showone/' + table + "/" + unique_ref
		item['href'] = getCurrentPath(url, mod_path)
		#row_item={}
		data = []
		row_item_data={}
		counter=0
		for x in column_flags:
			temp={}
			temp['name']= str(x[0])
			temp['value']= str(i[counter])
			#row_item_data['{0}'.format(x[0])] = i[counter]
			data.append(temp)
			
			counter=counter+1

		#data.append(row_item_data)
		item['data'] = data
		
		collection.appendItem(item)

	return packageResponse(collection)

@app.errorhandler(404)
@app.errorhandler(500)
@app.route('/error')
def error(e):
	url = request.url
	collection = createSkeleton(url)
	collection['collection']['links'].append(generateLink(getCurrentPath(url, '/table/list'), 'list tables'))
	collection['collection']['links'].append(generateLink(getCurrentPath(url, '/table/<table>'), '[GET] describe table'))
	collection['collection']['links'].append(generateLink(getCurrentPath(url, '/table/showall/<table>'), 'show all from table'))
	collection['collection']['links'].append(generateLink(getCurrentPath(url, '/table/showone/<table>/<unique_href>'), 'show one from table'))
	collection['collection']['links'].append(generateLink(getCurrentPath(url, '/table/<table>'), '[POST] post to table'))
	collection['collection']['error'] = generateError("API:None", "IE x0005", "API link does not exist")
	if (e == 404):
		return packageResponse(collection)
	else:
		return packageResponse(collection)



if __name__ == '__main__':
    app.run(debug=True, port=5000)