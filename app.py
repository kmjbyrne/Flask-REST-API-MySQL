from flask import Flask,render_template,jsonify,url_for,request,session,flash
from collection_json import Collection
from werkzeug import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from functools import wraps
import MySQLdb



app = Flask(__name__)

#######################
### CONFIG SETTINGS ###
#######################

host = 'localhost'
password = 'root'
user = 'root'
db = "GamesDB"


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


@app.route('/')
def root():
	return render_template("test.html")

def dictifyTableItem(data):
	
	table_name = data[0]
	href = "http://localhost:5000/api/table/structure/" + table_name
	data = []
	data.append({"name": "text", "value": table_name})

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

	


@app.route('/api/table/list', methods=['GET', 'POST'])
def getTableList():
	print("HERE 1")
	#Function for retrieving table list
	query = "SHOW TABLES"
	print("HERE 2")
	data = runSQLQuery(query, 0)
	print(data)

	print(collection)
	tables = []
	for i in data:
		print(i[0])
		collection['collection']['items'].append(dictifyTableItem(i))
	

	print(collection.items)

	print(collection)

	return jsonify(collection)


@app.route('/api/table/structure/<table_definition>', methods=['GET'])
def returnTableStructure(table_definition):
	input_table = request.get_data()
	print(input_table)
	query = "DESCRIBE {0}".format(table_definition)
	data = runSQLQuery(query, 0)

	collection = collectionTemplate()

	x = 0
	for i in data:
		print(i)
		collection['collection']['items'].append(dictifyDescribleTable(i, x))
		x = x+1

	return jsonify(collection)





if __name__ == '__main__':
    app.run(debug=True)