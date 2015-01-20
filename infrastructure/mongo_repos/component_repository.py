__author__ = 'Dani'

from webindex.domain.model.component import Repository
from config import port, db_name, host
from .mongo_connection import connect_to_db
from utils import normalize_group_name


class ComponentRepository(Repository):
    """Concrete mongodb repository for Component.
    """

    def __init__(self, url_root):
        self._db = connect_to_db(host=host, port=port, db_name=db_name)
        self._url_root = url_root

    def insert_component(self, component, component_uri=None, subindex_name=None, index_name=None, weight=None,
                         provider_name=None, provider_url=None):
        component_dict = {}
        component_dict['_id'] = component.id
        component_dict['index'] = normalize_group_name(index_name)
        component_dict['subindex'] = normalize_group_name(subindex_name)
        component_dict['component'] = None
        component_dict['indicator'] = normalize_group_name(component.label)
        component_dict['name'] = component.label
        component_dict['description'] = component.comment
        component_dict['type'] = component.type
        component_dict['parent'] = normalize_group_name(subindex_name)
        component_dict['uri'] = component_uri
        component_dict['weight'] = weight
        component_dict['republish'] = True
        component_dict['provider_name'] = provider_name
        component_dict['provider_url'] = provider_url

        self._db['indicators'].insert(component_dict)  # This is OK. it will be stored in "indicators"

