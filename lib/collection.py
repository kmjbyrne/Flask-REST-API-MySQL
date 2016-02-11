
from urlparse import urlparse

api_root = '/api/'

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