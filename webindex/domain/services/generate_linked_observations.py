from pyld import jsonld
import json
import requests

observations_context = {
    "scored": {"@id": "http://purl.org/weso/ontology/computex#RankingScore", "@type": "@id"},
    "indicator:": {"@id": "http://purl.org/weso/ontology/computex#Indicator", "@type": "@id"},
    "area_name:": {"@id": "http://schema.org/Country", "@type": "@id"},
    "ranked:": {"@id": "http://purl.org/weso/ontology/computex#Ranked", "@type": "@id"},
    "normalized": {"@id": "http://purl.org/weso/ontology/computex#Normalized", "@type": "@id"},
    "continent": {"@id": "http://schema.org/Continent", "@type": "@id"}}


r = requests.get('http://intertip.webfoundation.org/api/observations')
observations = r.json()


def get_observations():
    for observation in observations['data']:
        yield observation


def annotate_observations():
    for obs in get_observations():
        obs['@id'] = obs.pop('uri')
        obs['http://purl.org/weso/ontology/computex#Indicator'] = obs.pop('indicator')
        obs['http://purl.org/weso/ontology/computex#Ranked'] = obs.pop('ranked')
        obs['http://purl.org/weso/ontology/computex#Normalized'] = obs.pop('normalized')
        obs['http://schema.org/Continent'] = obs.pop('continent')
        obs['http://schema.org/Country'] = obs.pop('area_name')
        yield obs


def compact_json():
    with open('linked_observations.json', mode='w') as compacted:
        compacted.write(json.dumps(jsonld.compact(observations, observations_context)) + "\n")
        compacted.write("%s" % ",\n".join([json.dumps(obj) for obj in annotate_observations()]))


if __name__ == '__main__':
    annotate_observations()
    compact_json()