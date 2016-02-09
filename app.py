from flask import Flask,render_template,jsonify,url_for,request,session,flash, json
from collections import OrderedDict
from requests import put, get
from werkzeug import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from functools import wraps
import MySQLdb



# HTTP Request Detail
# TYPE : API Feature

# GET /table/list
# GET /table/structure
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


def collectionTemplate():
	collection = 	{
						"collection":{
							"version": "1.0",
							"href": "http://localhost:5000/api/table/list",
							"items": [],
							"links": []
						}
					}
	return collection

def runSQLQuery(_sql, code):
    con = MySQLdb.connect(host, user, password, db)
    cursor = con.cursor()

    if code == 0: # All select queries here
        cursor.execute(_sql)
        data = cursor.fetchall()
        return data


    elif code == 1: #All insert queries here
        try:
            cursor.execute(_sql)
            con.commit()
            return True
        except Exception as e:
            print(str(e))
            return False

    cursor.close()
    con.close()

def dictifyTableItem(data):
	
	value = data[0]
	href = "http://localhost:5000/api/table/structure/" + value
	data = []
	data.append({"database": value})

	dict = 	{	"href": href,
				"data": data	
			}

	return dict

def dictifyDescribleTable(data, id):
	print(data)
	field_name = data[0]
	type = data[1]
	nullable = data[2]
	key = data[3]
	default = data[4]
	extra = data[5]

	data = []
	data.append(
		{"field": field_name, 
		"type": type,
		"nullable": nullable,
		"key": key,
		"default": default,
		"extra": extra})

	href = "http://localhost:5000/api/table/structure/field_" + str(id)

	dict = 	{ 	"href": href,
				"data": data
			}

	return dict

def generateDynamicItem(columns, data):
	items = []
	counter = 0
	outer = 0

	for i in data:
		for x in i:
			dict = {'value': x[0]}
			items.append(dict)

	return jsonify(items)


@app.route('/')
def root():
	collection = collectionTemplate()
	query="SHOW DATABASES"
	data = runSQLQuery(query, 0)
	print(data)

	return render_template("index.html")

@app.route('/api/table/list', methods=['GET', 'POST'])
def getTableList():

	#Function for retrieving table list
	query = "SHOW TABLES"

	data = runSQLQuery(query, 0)


	collection = collectionTemplate()

	for i in data:
		collection['collection']['items'].append(dictifyTableItem(i))
	

	print(json.dumps(collection))
	return jsonify(collection)


@app.route('/api/table/structure/<table>', methods=['GET'])
def returnTableStructure(table):
	input_table = request.get_data()
	print(input_table)
	query = "DESCRIBE {0}".format(table)
	data = runSQLQuery(query, 0)

	collection = collectionTemplate()

	x = 0
	for i in data:
		print(i)
		collection['collection']['items'].append(dictifyDescribleTable(i, x))
		x = x+1

	return jsonify(collection)

@app.route('/api/showone/<table_definition>', methods=['GET'])
def showone(table_definition):

	query = "SELECT * FROM {0}".format(table_definition)
	column_query = "SHOW COLUMNS FROM {0}".format(table_definition)
	data = runSQLQuery(query, 0)
	data_res = runSQLQuery(column_query, 0)
	print(data)

	collection = collectionTemplate()
	collection['collection']['items'].append(generateDynamicItem(data_res, data))

	return jsonify(collection)

if __name__ == '__main__':
    app.run(debug=True)