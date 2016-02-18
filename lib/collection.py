
from urlparse import urlparse

api_root = '/table/list/'

class Structure(object):
    def __init__(self, url):
        #Creates new Collection+JSON template object
        pu = urlparse(url)
        base = pu.scheme + "://" + pu.netloc
        path = pu.path

        self.collection = {}
        self.collection['collection'] = {}
        self.collection['collection']['version'] = "1.0"
        self.collection['collection']['href'] = base + path
        self.collection['collection']['links'] = linksDefault(base + api_root)
        self.collection['collection']['items'] = []
        self.collection['collection']['queries'] = []
        self.collection['collection']['template'] = {}

    def appendItem(self, item):
        self.collection['collection']['items'].append(item)

    def getCollection(self):
        return self.collection

    def appendLink(self, link):
        self.collection['collection']['links'].append(link)

    def setItems(self, items):
        self.collection['collection']['items'] = items

    def setPostTemplate(self, template):
        self.collection['collection']['template'] = template

    def setError(self, error):
        self.collection['collection']['error'] = error


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

def get_skeleton(url):
    pu = urlparse(url)
    base = pu.scheme + "://" + pu.netloc
    path = pu.path

    links = []
    dict = {'rel': 'home', 'href': path}
    links.append(dict)

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