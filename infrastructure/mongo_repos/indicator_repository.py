__author__ = 'guillermo'


from infrastructure.errors.errors import IndicatorRepositoryError
from a4ai.domain.model.indicator.indicator import Repository, Indicator
from config import port, db_name, host
from .mongo_connection import connect_to_db
from utils import error, success, uri, normalize_group_name
from a4ai.domain.model.indicator.indicator import create_indicator


class IndicatorRepository(Repository):
    """
    Concrete mongodb repository for Indicators.
    """

    def __init__(self, url_root):
        """
        Constructor for IndicatorRepository

        Args:
            url_root (str): URL root where service is deployed, it will be used to compose URIs on areas
        """
        self._db = connect_to_db(host=host, port=port, db_name=db_name)
        self._url_root = url_root

    def find_indicator_by_code(self, indicator_code):
        """
        Finds a indicator by its code, in this case the indicator attribute

        Args:
            indicator_code (str): Code of the indicator to query

        Returns:
            Indicator: The first indicator with the given code

        Raises:
            IndicatorRepositoryError: If there is not an indicator with the given code
        """
        indicator_code = indicator_code.upper()
        indicator = self._db['indicators'].find_one({"indicator": indicator_code})

        if indicator is None:
            raise IndicatorRepositoryError("No indicator with code " + indicator_code)

        children = self.find_indicator_children(indicator)
        indicator["children"] = children

        return IndicatorDocumentAdapter().transform_to_indicator(indicator)

    def find_indicators(self):
        """
        Finds all indicators

        Returns:
            list of Indicator: All the indicators stored
        """
        _index = self.find_indicators_index()
        subindices = self.find_indicators_sub_indexes()
        indicators = self.find_indicators_indicators()

        result = (_index + subindices + indicators)
        return result

    def find_indicators_index(self):
        """
        Finds all indicators whose type is Index

        Returns:
            list of Indicator: Indicators with type Index
        """
        return self.find_indicators_by_level("Index")

    def find_indicators_sub_indexes(self):
        """
        Finds all indicators whose type is SubIndex

        Returns:
            list of Indicator: Indicators with type SubIndex
        """
        return self.find_indicators_by_level("SubIndex")


    def find_indicators_primary(self, parent=None):
        """
        Finds all indicators whose type is Primary

        Returns:
            list of Indicator: Indicators with type Primary
        """
        return self.find_indicators_by_level("Primary", parent)

    def find_indicators_secondary(self, parent=None):
        """
        Finds all indicators whose type is Secondary

        Returns:
            list of Indicator: Indicators with type Secondary
        """
        return self.find_indicators_by_level("Secondary", parent)

    def find_indicators_indicators(self, parent=None):
        """
        Finds all indicators whose type is Primary or Secondary

        Returns:
            list of Indicator: Indicators with type Primary or Secondary
        """
        primary = self.find_indicators_primary(parent)
        secondary = self.find_indicators_secondary(parent)

        result = (primary + secondary)
        return result

    def find_indicators_by_level(self, level, parent=None):
        """
        Finds indicators whose type is equals to the given level, e.g.: Index, SubIndex, Primary or Secondary

        Args:
            level (str): Type of the indicators to search
            parent (Indicator, optional): Parent indicator if more filter is required, default to None

        Returns:
            list of Indicator: Indicators that fit with the given filters
        """
        search = {"type": level}

        if parent is not None:
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
            processed_indicators.append(indicator)

        return IndicatorDocumentAdapter().transform_to_indicator_list(processed_indicators)

    def find_indicator_children(self, indicator):
        """
        Finds the children of the given indicator

        Args:
            indicator (Indicator): Parent indicator

        Returns:
            list of Indicator: The children of the indicator
        """
        # TODO: These queries may change due to change in data
        if indicator['type'] == 'Index':
            indicators = self._db["indicators"].find({"$and":
                                                      [{"index": indicator['indicator']},
                                                       {"type": "SubIndex"}]})
        elif indicator['type'] == 'SubIndex':
            indicators = self._db["indicators"].find({"$and":
                                                          [{"subindex": indicator['indicator']},
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

    def insert_indicator(self, indicator, indicator_uri=None, component_name=None, subindex_name=None, index_name=None,
                         weight=None, provider_name=None, provider_url=None, is_percentage=None, scale=None):
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
        indicator_dict['is_percentage'] = is_percentage
        indicator_dict['scale'] = scale

        self._db['indicators'].insert(indicator_dict)

    def update_indicator_weight(self, indicator_code, weight=None):
        indicator = self.find_indicator_by_code(indicator_code)
        if indicator["success"]:
            indicator = indicator["data"]
            indicator['weight'] = weight
            self._db['indicators'].update({'_id': indicator["_id"]}, {"$set": indicator}, upsert=False)


class IndicatorDocumentAdapter(object):
    """
    Adapter class to transform indicators from PyMongo format to Domain indicator objects
    """
    def transform_to_indicator(self, indicator_document):
        """
        Transforms one single indicator

        Args:
            indicator_document (dict): Indicator document in PyMongo format

        Returns:
            Indicator: Indicator object with the data in indicator_document
        """
        return create_indicator(id=indicator_document['_id'],
                                index=indicator_document['index'],
                                indicator=indicator_document['indicator'],
                                name=indicator_document['name'],
                                parent=indicator_document['parent'],
                                subindex=indicator_document['subindex'],
                                type=indicator_document['type'],
                                provider_url=indicator_document['provider_url'],
                                description=indicator_document['description'],
                                uri=indicator_document['uri'],
                                provider_name=indicator_document['provider_name'],
                                republish=indicator_document['republish'],
                                children=self.transform_to_indicator_list(indicator_document['children']),
                                is_percentage=indicator_document['is_percentage'])

    def transform_to_indicator_list(self, indicator_document_list):
        """
        Transforms a list of indicators

        Args:
            indicator_document_list (list): Indicator document list in PyMongo format

        Returns:
            list of Indicator: A list of indicators with the data in indicator_document_list
        """
        return [self.transform_to_indicator(indicator_document) for indicator_document in indicator_document_list]
