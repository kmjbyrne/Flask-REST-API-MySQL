
def getHTTPError(error_code, request):
	item = {}
	if(error_code == 405):
		item['title'] = "Invalid HTTP REQUEST"
		item['code'] = "HTTP:405"
		item['message'] = "IS TYPE: " + request.method + " - Check HTTP method!"
	return item

def getError(error_code, msg):
	item = {}
	item['title'] = ""
	item['code'] = ""
	item['message'] = ""

	if(error_code == 1):
		item['title'] = "No data given"
		item['code'] = "IE x0001"
		item['message'] = "JSON package is None"
	elif(error_code == 2):
		item['title'] = "Cannot insert"
		item['code'] = "IE x0002"
		item['message'] = "" + str(msg)
	elif(error_code == 3):
		item['title'] = "Does not exist"
		item['code'] = "IE x0003"
		item['message'] = "Item HREF does not correspond to any data"
	elif(error_code == 4):
		item['title'] = "No data given"
		item['code'] = "IE x0004"
		item['message'] = "JSON package is None"
	elif(error_code == 6):
		item['title'] = "Not found"
		item['code'] = "HTTP:404"
		item['message'] = "Page/API resource not found. See API reference."
	elif(error_code == -1):
		item['title'] = "General Error"
		item['code'] = "IE x0000"
		item['message'] = "" + str(msg)
	elif(error_code ==5):
		item['title'] = "DB Connection Error"
		item['code'] = "IE x0005"
		item['message'] = "" + str(msg)


	return item