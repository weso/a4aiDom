__author__ = 'guillermo'

from rdflib import Namespace, URIRef

# Namespaces
schema = Namespace("http://schema.org/")
cex = Namespace("http://purl.org/weso/computex/ontology#")
dct = Namespace("http://purl.org/dc/terms/")
dctype = Namespace("http://purl.org/dc/dcmitype/")
foaf = Namespace("http://xmlns.com/foaf/0.1/")
lb = Namespace("http://purl.org/weso/landbook/ontology#") # Check this
org = Namespace("http://www.w3.org/ns/org#")
qb = Namespace("http://purl.org/linked-data/cube#")
sdmx_concept = Namespace("http://purl.org/linked-data/sdmx/2009/concept#")
time = Namespace("http://www.w3.org/2006/time#")
sdmx_code = Namespace("http://purl.org/linked-data/sdmx/2009/code#")

base = Namespace("http://data.webfoundation.org/webindex/v2014/")
base_time = Namespace("http://data.webfoundation.org/webindex/v2014/time/")
base_obs = Namespace("http://data.webfoundation.org/webindex/v2014/observation/")
base_obs_uri = Namespace("http://data.webfoundation.org/webindex/v2014/observation/uri_api/")
base_ind = Namespace("http://data.webfoundation.org/webindex/v2014/indicator/")
base_area = Namespace("http://data.webfoundation.org/webindex/v2014/area/")
base_org = Namespace("http://data.webfoundation.org/webindex/v2014/organization/")

dcat = Namespace("http://www.w3.org/ns/dcat#")


def bind_namespaces(graph):
    """
    Binds Webindex uris with their corresponding prefixes
    """
    n_space = {"cex": cex, "dct": dct, "dctype": dctype, "foaf": foaf,
               "lb": lb, "org": org, "qb": qb, "sdmx-concept": sdmx_concept, "time": time,
               "sdmx-code": sdmx_code, "": base, "base-obs": base_obs,
               "base-ind": base_ind, "base-org": base_org, "base-time": base_time,
               "dcat": dcat}

    for prefix, uri in n_space.items():
        graph.namespace_manager.bind(prefix, URIRef(Namespace(uri)))