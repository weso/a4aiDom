from namespaces_handler import *
from rdflib.namespace import RDF, RDFS, XSD
from rdflib import Literal, Graph

__author__ = 'miguel'


class RDFService(object):

    def __init__(self, area_repository, indicator_repository):
        self._area_repository = area_repository
        self._indicator_repository = indicator_repository

    def generate_dataset(self, observations):
        graph = Graph()
        for observation in observations:
            self._add_observation_triples(observation, graph)
        serialized = graph.serialize(format='application/rdf+xml')
        with open("dataset.rdf", 'w') as dataset:
            dataset.write(serialized)
        return graph  # We will see if this is the thing to return or not

    def _add_observation_triples(self, observation, graph):
        #### Initializing observation term
        observation_term = cex.term(self._build_observation_id(observation))

        #### Adding Literal and type triples
        graph.add((observation_term,
                  RDF.type,
                  cex.term("Observation")))

        graph.add((observation_term,
                  RDFS.label,
                  Literal(self._build_observation_label(observation), lang="en")))

        graph.add((observation_term,
                  base_obs_uri.term("uri_api"),
                  Literal(observation['uri'])))

        graph.add((observation_term,
                  cex.term("Raw"),
                  Literal(observation['value'], datatype=XSD.double)))

        if observation['normalized'] is not None:
            graph.add((observation_term,
                      cex.term("Normalized"),
                      Literal(observation['normalized'], datatype=XSD.double)))

        if observation['scored'] is not None:
            graph.add((observation_term,
                      cex.term("RankingScore"),
                      Literal(observation['scored'], datatype=XSD.double)))

        if observation['ranked'] is not None:
            graph.add((observation_term,
                      cex.term("Ranked"),
                      Literal(observation['ranked'], datatype=XSD.integer)))


        #### Linking observation with other subjects

            graph.add((observation_term,
                      cex.term("ref-indicator"),
                      base_ind.term(observation['indicator'])))

            graph.add((observation_term,
                      cex.term("ref-year"),
                      base_time.term(observation['year'])))

            graph.add((observation_term,
                      cex.term("ref-area"),
                      base_area.term(observation['area'])))

            graph.add((observation_term,
                       schema.term("Continent"),
                       Literal(observation['continent'])))

    @staticmethod
    def _build_observation_id(observation_dict):
        return "OBS_{}_{}_{}".format(observation_dict["indicator"],
                                     observation_dict["area"],
                                     observation_dict["year"])

    @staticmethod
    def _build_observation_label(observation_dict):
        return "Observation for {} over the indicator {} during {}".format(observation_dict["area"],
                                                                           observation_dict['indicator'],
                                                                           observation_dict['year'])