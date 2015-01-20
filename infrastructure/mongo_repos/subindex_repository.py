__author__ = 'Dani'

from webindex.domain.model.subindex import Repository
from config import port, db_name, host
from .mongo_connection import connect_to_db
from utils import normalize_group_name


class SubindexRepository(Repository):
    """Concrete mongodb repository for Component.
    """

    def __init__(self, url_root):
        self._db = connect_to_db(host=host, port=port, db_name=db_name)
        self._url_root = url_root

    def insert_subindex(self, subindex, subindex_uri=None, index_name=None, weight=None,
                        provider_name=None, provider_url=None):
        subindex_dict = {}
        subindex_dict["_id"] = subindex.id
        subindex_dict["index"] = normalize_group_name(index_name)
        subindex_dict['component'] = None
        subindex_dict['subindex'] = None
        subindex_dict['indicator'] = normalize_group_name(subindex.label)
        subindex_dict['name'] = subindex.label
        subindex_dict['description'] = subindex.comment
        subindex_dict['type'] = subindex.type
        subindex_dict['parent'] = normalize_group_name(index_name)
        subindex_dict['uri'] = subindex_uri
        subindex_dict['weight'] = weight
        subindex_dict['republish'] = True
        subindex_dict['provider_name'] = provider_name
        subindex_dict['provider_url'] = provider_url

        self._db['indicators'].insert(subindex_dict)
