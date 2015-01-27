import json

__author__ = 'guillermo'
from webindex.domain.model.indicator.indicator import Repository, Indicator
from config import port, db_name, host
from .mongo_connection import connect_to_db
from utils import error, success, uri, normalize_group_name
from webindex.domain.model.indicator.indicator import create_indicator


class IndicatorRepository(Repository):
    """Concrete mongodb repository for Indicators.
    """

    def __init__(self, url_root):
        self._db = connect_to_db(host=host, port=port, db_name=db_name)
        self._url_root = url_root

    def find_indicators_by_code(self, indicator_code):
        indicator_code = indicator_code.upper()
        indicator = self._db['indicators'].find_one({"indicator": indicator_code})

        if indicator is None:
            return self.indicator_error(indicator_code)

        children = self.find_indicator_children(indicator)
        indicator["children"] = children
        # self.indicator_uri(indicator)

        return IndicatorDocumentAdapter().transform_to_indicator(indicator)

    def find_indicators(self):
        _index = self.find_indicators_index()
        subindices = self.find_indicators_sub_indexes()
        #components = self.find_indicators_components()
        indicators = self.find_indicators_indicators()

        #result = (_index + subindices + components + indicators)
        result = (_index + subindices + indicators)
        return result

    def find_indicators_index(self):
        return self.find_indicators_by_level("Index")

    def find_indicators_sub_indexes(self):
        return self.find_indicators_by_level("Subindex")

    #def find_indicators_components(self, parent=None):
    #    return self.find_indicators_by_level("Component", parent)

    def find_indicators_primary(self, parent=None):
        return self.find_indicators_by_level("Primary", parent)

    def find_indicators_secondary(self, parent=None):
        return self.find_indicators_by_level("Secondary", parent)

    def find_indicators_indicators(self, parent=None):
        primary = self.find_indicators_primary(parent)
        secondary = self.find_indicators_secondary(parent)

        result = (primary + secondary)
        return result

    def find_indicators_by_level(self, level, parent=None):
        search = {"type": level}

        if parent is not None:
            # print parent
            code = parent.indicator
            _type = parent.type.lower()
            _filter = {}
            _filter[_type] = code
            search = {"$and": [search, _filter]}

        indicators = self._db["indicators"].find(search)

        processed_indicators = []

        for indicator in indicators:
            code = indicator["indicator"]
            children = self.find_indicator_children(indicator)
            indicator["children"] = children
            # self.indicator_uri(indicator)
            processed_indicators.append(indicator)

        #return success(processed_indicators)
        return IndicatorDocumentAdapter().transform_to_indicator_list(processed_indicators)

    def find_indicator_children(self, indicator):
        # TODO: These queries may change due to change in data
        if indicator['type'] == 'Index':
            indicators = self._db["indicators"].find({"$and":
                                                      [{"index": indicator['indicator'].upper()},
                                                       {"type": "Subindex"}]})
        elif indicator['type'] == 'Subindex':
            indicators = self._db["indicators"].find({"$and":
                                                          [{"subindex": indicator['indicator'].upper()},
                                                           {"$or": [{"type": "Primary"}, {"type": "Secondary"}]}]})

        else:
            return []

        processed_indicators = []

        for indicator in indicators:
            code = indicator["indicator"]
            children = self.find_indicator_children(indicator)
            indicator["children"] = children
            self.indicator_uri(indicator)
            processed_indicators.append(indicator)

        return processed_indicators

    def indicator_error(self, indicator_code):
        return error("Invalid Indicator Code: %s" % indicator_code)

    # def indicator_uri(self, indicator_code):
    #     uri(url_root=self._url_root, element=indicator_code,
    #         element_code="indicator", level="indicators")

    def insert_indicator(self, indicator, indicator_uri=None, component_name=None, subindex_name=None, index_name=None,
                         weight=None, provider_name=None, provider_url=None):
        indicator_dict = {}
        indicator_dict["index"] = normalize_group_name(index_name)
        indicator_dict["subindex"] = normalize_group_name(subindex_name)
        indicator_dict["indicator"] = indicator.indicator
        indicator_dict["name"] = indicator.name
        indicator_dict["description"] = indicator.description
        indicator_dict["type"] = indicator.type
        indicator_dict["parent"] = normalize_group_name(component_name)
        indicator_dict['uri'] = indicator_uri
        indicator_dict['republish'] = indicator.republish
        indicator_dict['provider_name'] = provider_name
        indicator_dict['provider_url'] = provider_url

        self._db['indicators'].insert(indicator_dict)

    def update_indicator_weight(self, indicator_code, weight=None):
        indicator = self.find_indicators_by_code(indicator_code)
        if indicator["success"]:
            indicator = indicator["data"]
            indicator['weight'] = weight
            self._db['indicators'].update({'_id': indicator["_id"]}, {"$set": indicator}, upsert=False)


class IndicatorDocumentAdapter(object):

    def transform_to_indicator(self, indicator_document):
        return create_indicator(id=indicator_document['_id'],
                         index=indicator_document['index'], indicator=indicator_document['indicator'],
                         name=indicator_document['name'], parent=indicator_document['parent'],
                         #component=indicator_document['component'],
                         subindex=indicator_document['subindex'],
                         type=indicator_document['type'], provider_url=indicator_document['provider_url'],
                         description=indicator_document['description'], uri=indicator_document['uri'],
                         #weight=indicator_document['weight'],
                         provider_name=indicator_document['provider_name'],
                         republish=indicator_document['republish'],
                         children=self.transform_to_indicator_list(indicator_document['children']),
                         #high_low=indicator_document['high_low'] if 'high_low' in indicator_document else None
                         )

    def transform_to_indicator_list(self, indicator_document_list):
        return [self.transform_to_indicator(indicator_document) for indicator_document in indicator_document_list]
