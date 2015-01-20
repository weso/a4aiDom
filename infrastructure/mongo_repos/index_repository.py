__author__ = 'Dani'

from webindex.domain.model.index import Repository
from config import port, db_name, host
from .mongo_connection import connect_to_db
from utils import normalize_group_name


class IndexRepository(Repository):
    """Concrete mongodb repository for Component.
    """

    def __init__(self, url_root):
        self._db = connect_to_db(host=host, port=port, db_name=db_name)
        self._url_root = url_root

    def insert_index(self, index, index_uri=None, provider_name=None, provider_url=None):
        index_dict = {}
        index_dict['_id'] = index.id
        index_dict["index"] = None
        index_dict['subindex'] = None
        index_dict['component'] = None
        index_dict['indicator'] = normalize_group_name(index.label)
        index_dict['name'] = index.label
        index_dict['description'] = index.comment
        index_dict['type'] = index.type
        index_dict['parent'] = None
        index_dict['uri'] = index_uri
        index_dict['weight'] = 1
        index_dict['republish'] = True
        index_dict['provider_name'] = provider_name
        index_dict['provider_url'] = provider_url

        self._db['indicators'].insert(index_dict)
