import filemanagement as fm
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

## Export query result
def get_select_query_wikidata(query:str):
    endpoint_url = "https://query.wikidata.org/sparql"
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def construct_table_results_from_json(json_query_results):
    """
    From the result of a query whose type is JSON, convert it in CSV format
    sep defines separators between values 
    """
    header = json_query_results.get("head").get("vars")
    results = json_query_results.get("results").get("bindings")

    rows = [header]

    for result in results:
        row = ["" for x in header]
        for key, value in result.items():
            index = header.index(key)
            val = value.get("value")
            row[index] = val
        rows.append(row)

    return rows

def save_select_query_as_csv_file(query:str, filename:str):
    results = get_select_query_wikidata(query)
    rows = construct_table_results_from_json(results)
    fm.write_csv_file_from_rows(rows, filename)