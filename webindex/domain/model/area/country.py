__author__ = 'guillermo'

from webindex.domain.model.entity import Entity


class Country(Entity):
    """ Country entity """

    def __init__(self, event, region):
        super(Country, self).__init__(event.country_id, event.country_version)
        self._region = region
        self._type = "Country"
        self._iso2_code = event.iso2_code
        self._iso3_code = event.iso3_code
        self._label = event.label

    def __repr__(self):
        return "{d}Country(id={id!r}, region_id={c._region.id!r}, " \
               "iso2_code={c._iso2_code}, iso3_code={c._iso3_code}, label={c._label!r})".\
                format(d="Discarded" if self.discarded else "", id=self._id, c=self,
                       type=self._type)

# =======================================================================================
# Properties
# =======================================================================================
    @property
    def iso2_code(self):
        self._check_not_discarded()
        return self._iso2_code

    @iso2_code.setter
    def iso2_code(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Country iso2_code cannot be empty")
        self._iso2_code = value
        self.increment_version()

    @property
    def iso3_code(self):
        self._check_not_discarded()
        return self._iso3_code

    @iso3_code.setter
    def iso3_code(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Country iso3_code cannot be empty")
        self._iso3_code = value
        self.increment_version()

    @property
    def label(self):
        self._check_not_discarded()
        return self._label

    @label.setter
    def label(self, value):
        self._check_not_discarded()
        if len(value) < 1:
            raise ValueError("Country label cannot be empty")
        self._label = value
        self.increment_version()