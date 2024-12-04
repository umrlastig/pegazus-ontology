import os
import glob
import json
import requests
import urllib.parse as up
from rdflib import Graph, Namespace, Literal, BNode, URIRef
from rdflib.namespace import RDF

def get_repositories(graphdb_host,proxies):
    """
    Get the list of repositories of a Graph DB triplestore.
    """
    url = f"{graphdb_host}/rest/repositories"
    response = requests.request("GET", url, proxies=proxies)
    print(url)
    return response

def set_default_repository(graphdb_host,repository,proxies):
    """
    Define the default repository of a Graph DB triplestore.
    """
    json_data = {
        'repository': repository,
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(f'{graphdb_host}/rest/locations/active/default-repository', headers=headers, json=json_data, proxies=proxies)
    return response

def load_ttl_files_into_named_graph(GRAPHDB_HOST,GRAPHDB_REPO,RDF_PATH,NAMED_GRAPHS_AND_RDF_FILES,proxies):
    """
    Load Turtle files in first column of NAMED_GRAPHS_AND_RDF_FILES located in folder RDF_PATH 
    into the named graphs in the NAMED_GRAPHS_AND_RDF_FILES list in a given GRAPHDB_REPO.
    """
    headers = {
        'Content-Type': 'application/x-turtle',
    }
    url = f"{GRAPHDB_HOST}/repositories/{GRAPHDB_REPO}/statements"

    for elem in NAMED_GRAPHS_AND_RDF_FILES:
        file = elem[0]
        named_graph = elem[1]
        encoded_named_graph_uri = up.quote(URIRef(named_graph).n3())

        with open(RDF_PATH + '/' + file, 'rb') as f:
            data = f.read()

        final_url = url + "?context=" + encoded_named_graph_uri
        response = requests.post(final_url, headers=headers, data=data, proxies=proxies)
        print(response.text)

def remove_named_graphs(GRAPHDB_HOST,GRAPHDB_REPO,NAMED_GRAPHS,proxies):
    """
    Delete named graphs of a given list from a given GRAPHDB_REPO.
    """
    
    headers = {
        'Content-Type': 'application/x-turtle',
    }

    url = f"{GRAPHDB_HOST}/repositories/{GRAPHDB_REPO}/statements"

    for g in NAMED_GRAPHS:
        final_url = url + "?context=" + up.quote(URIRef(g).n3())
        response = requests.request("DELETE", final_url, headers=headers, proxies=proxies)
        response

def update_sparql_query(GRAPHDB_HOST,GRAPHDB_REPO,QUERY,proxies):
  url = f"{GRAPHDB_HOST}/repositories/{GRAPHDB_REPO}/statements"
  query_encoded = up.quote(QUERY)
  response = requests.request("POST", url, data=f"update={query_encoded}", headers={'Content-Type': 'application/x-www-form-urlencoded'}, proxies=proxies)
  print(response, response.text)