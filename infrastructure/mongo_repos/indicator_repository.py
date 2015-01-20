__author__ = 'guillermo'
from webindex.domain.model.indicator.indicator import Repository
from config import port, db_name, host
from .mongo_connection import connect_to_db
from utils import error, success, uri, normalize_group_name, normalize_high_low


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

        children = self.find_indicator_children(indicator_code)
        indicator["children"] = children
        # self.indicator_uri(indicator)

        return success(indicator)

    def find_indicators(self):
        _index = self.find_indicators_index()["data"]
        subindices = self.find_indicators_sub_indexes()["data"]
        components = self.find_indicators_components()["data"]
        indicators = self.find_indicators_indicators()["data"]

        return success(_index + subindices + components + indicators)

    def find_indicators_index(self):
        return self.find_indicators_by_level("Index")

    def find_indicators_sub_indexes(self):
        return self.find_indicators_by_level("Subindex")

    def find_indicators_components(self, parent=None):
        return self.find_indicators_by_level("Component", parent)

    def find_indicators_primary(self, parent=None):
        return self.find_indicators_by_level("Primary", parent)

    def find_indicators_secondary(self, parent=None):
        return self.find_indicators_by_level("Secondary", parent)

    def find_indicators_indicators(self, parent=None):
        primary = self.find_indicators_primary(parent)["data"]
        secondary = self.find_indicators_secondary(parent)["data"]

        return success(primary + secondary)

    def find_indicators_by_level(self, level, parent=None):
        search = {"type": level}

        if parent is not None:
            print parent
            code = parent["indicator"]
            _type = parent["type"].lower()
            _filter = {}
            _filter[_type] = code
            search = {"$and": [search, _filter]}

        indicators = self._db["indicators"].find(search)

        processed_indicators = []

        for indicator in indicators:
            code = indicator["indicator"]
            children = self.find_indicator_children(code)
            indicator["children"] = children
            # self.indicator_uri(indicator)
            processed_indicators.append(indicator)

        return success(processed_indicators)

    def find_indicator_children(self, indicator):
        indicators = self._db["indicators"].find({"parent": indicator})
        processed_indicators = []

        for indicator in indicators:
            code = indicator["indicator"]
            children = self.find_indicator_children(code)
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
        indicator_dict["_id"] = indicator.id
        indicator_dict["index"] = normalize_group_name(index_name)
        indicator_dict["subindex"] = normalize_group_name(subindex_name)
        indicator_dict["component"] = normalize_group_name(component_name)
        indicator_dict["indicator"] = indicator.code
        indicator_dict["name"] = indicator.label
        indicator_dict["description"] = indicator.comment
        indicator_dict["type"] = indicator.ind_type
        indicator_dict["parent"] = normalize_group_name(component_name)
        indicator_dict["high_low"] = normalize_high_low(indicator.high_low)
        indicator_dict['weight'] = weight
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


