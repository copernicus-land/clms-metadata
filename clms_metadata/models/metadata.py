import abc
import datetime
from pathlib import Path
from typing import Annotated, Any, Literal, Type

import ciso8601
from cloudpathlib import CloudPath
from geojson_pydantic.geometries import Geometry
from loguru import logger
from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PlainSerializer,
    field_validator,
)

from clms_metadata.constants.attributes import Attributes
from clms_metadata.models.name_list import Mission
from clms_metadata.util import format_zulu, partial_model


def parse_datetime(v: Any) -> datetime.datetime | Any:
    """
    Parse a string to a datetime object.
    If the object is not a string or cannot be parsed, the object will be returned as-is.

    :param v: value to parse
    :return: datetime object if parsed successfully, else original value
    """
    if isinstance(v, str):
        for parser in [
            lambda s: ciso8601.parse_datetime(s),
            lambda s: datetime.datetime.strptime(s, "%Y%m%dT%H:%M:%S%z"),
            lambda s: datetime.datetime.strptime(s, "%d-%b-%Y %H:%M:%S"),
            lambda s: datetime.datetime.strptime(s, "%Y%m%dT%H%M%S%z"),
        ]:
            try:
                dt = parser(v)
                return dt
            except ValueError:
                continue
    return v


def validate_utc(d: datetime.datetime) -> datetime.datetime:
    """
    Validate if the provided datetime is in UTC.
    If no timezone information is provided, the datetime is assumed to be in UTC and the timezone will be explicitly set on the datetime object.

    :param d: datetime to validate
    :return: datetime
    """
    if d.tzinfo is None:
        d = d.replace(tzinfo=datetime.timezone.utc)
    assert d.tzinfo == datetime.timezone.utc, "Expected datetime in UTC, got {}".format(
        d
    )
    return d


DateTimeUTC = Annotated[
    datetime.datetime,
    BeforeValidator(parse_datetime),
    AfterValidator(validate_utc),
    PlainSerializer(format_zulu),
]


class ContentDate(BaseModel):
    start: DateTimeUTC
    """Start of the sensing period in UTC"""

    end: DateTimeUTC
    """End of the sensing period in UTC"""


class Attribute(BaseModel, abc.ABC):
    name: str
    value_type: str
    value: Any


class StringAttribute(Attribute):
    value_type: Literal["String"] = "String"
    value: str | None


class IntegerAttribute(Attribute):
    value_type: Literal["Integer"] = "Integer"
    value: int


class DateTimeOffsetAttribute(Attribute):
    value_type: Literal["DateTimeOffset"] = "DateTimeOffset"
    value: DateTimeUTC


MANDATORY_ATTRIBUTES = {
    Attributes.PROCESSING_CENTER: StringAttribute,
    Attributes.DATASET_SHORT_NAME: StringAttribute,
    Attributes.DATASET_ALIAS: StringAttribute,
    Attributes.DATASET_VERSION: IntegerAttribute,
    Attributes.FILE_FORMAT: StringAttribute,
    Attributes.TEMPORAL_REPEAT_RATE: StringAttribute,
    Attributes.PRODUCT_VERSION: StringAttribute,
    Attributes.AREA_OF_INTEREST: StringAttribute,
    Attributes.MISSION_SHORT_NAME: StringAttribute,
    Attributes.PLATFORM_SHORT_NAME: StringAttribute,
    Attributes.PLATFORM_ACRONYM: StringAttribute,
    Attributes.INSTRUMENT_SHORT_NAME: StringAttribute,
}
OPTIONAL_ATTRIBUTES = {
    # only checked to have the following type when they are present
    Attributes.CONSOLIDATION_PERIOD: IntegerAttribute,
    Attributes.VPP_SEASON: StringAttribute,
    Attributes.METRIC_GRID_SPACING: IntegerAttribute,  # not applicable for GeoJSON datasets
    Attributes.GRID_LABEL: StringAttribute,  # not applicable for GeoJSON datasets
    Attributes.WATER_LEVEL_RIVER_NAME: StringAttribute,
    Attributes.WATER_LEVEL_LAKE_NAME: StringAttribute,
    Attributes.WATER_LEVEL_BASIN_NAME: StringAttribute,
}


def validate_attributes(attrs: list[Attribute]) -> list[Attribute]:
    """
    Check if mandatory attributes are present and optional attributes have the correct attribtue type.

    :param attrs: list of attributes
    :return: attributes
    """
    for attribute, atype in MANDATORY_ATTRIBUTES.items():
        assert (
            len(filtered := [attr for attr in attrs if attr.name == attribute]) == 1
        ), f"Expected attribute with name '{attribute}'"
        assert isinstance(
            filtered[0], atype
        ), f"Expected '{attribute}' attribute with value type {atype}"
    for attribute, atype in OPTIONAL_ATTRIBUTES.items():
        if len(filtered := [attr for attr in attrs if attr.name == attribute]) == 1:
            assert isinstance(
                filtered[0], atype
            ), f"Expected '{attribute}' attribute with value type {atype}"
    return attrs


AttributesType = Annotated[
    list[
        Annotated[
            StringAttribute | IntegerAttribute | DateTimeOffsetAttribute,
            Field(discriminator="value_type"),
        ]
    ],
    AfterValidator(validate_attributes),
]


class Metadata(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True, extra="allow")

    name: str
    """Data file name"""

    name_suffix: str | None
    """Product name suffix"""

    content_type: str
    """The MIME type of the product"""

    origin_date: DateTimeUTC
    """Date and time of the product at the source in UTC"""

    content_date: ContentDate
    """Sensing range period"""

    nominal_date: DateTimeUTC
    """Nominal date of the product"""

    geometry: Geometry
    """Geometry of the geo-referenced product"""

    path: Path | CloudPath
    """Path of the product"""

    product_type: str
    """Product type"""

    component: str
    """Component"""

    dataset_identifier: str
    """Dataset identifier"""

    attributes: AttributesType

    @field_validator("geometry", mode="before")
    @classmethod
    def set_geometry(cls, geometry: Any) -> Geometry:
        """
        Set geometry from geo interface or input

        :param geometry: geometry object
        """
        if hasattr(geometry, "__geo_interface__"):
            return geometry.__geo_interface__
        return geometry

    def has_attribute(self, name: str) -> bool:
        """
        Indicates whether the metadata includes an attribute with the given name.

        :param name: attribute name
        :return: boolean indicating whether the attribute already exists
        """
        return name in (attr.name for attr in self.attributes)

    def get_attribute(self, name: str) -> Attribute:
        """
        Get attribute by name.

        :param name: name of the attribute
        :return: attribute object
        """
        return next((a for a in self.attributes if a.name == name), None)

    def add_attribute(
        self,
        name: str,
        value_type: Type[Attribute],
        factory: callable,
        allow_none: bool = False,
    ):
        """
        Add an attribute to the attribute list in the metadata.

        :param name: attribute name
        :param value_type: type of the attribute value
        :param factory: method to extract the attribute value
        :param allow_none: allow attribute value to be None
        :return:
        """
        if not self.has_attribute(name) or not self.get_attribute(name).value:
            value = factory()
            if value is not None or allow_none:
                logger.debug("Adding attribute {}: {}", name, value)
                self.attributes.append(value_type(name=name, value=value))
            else:
                logger.debug("No value for attribute {}, skipping.", name)
        else:
            logger.debug("Attribute {} already exists, skipping.", name)


@partial_model
class PartialMetadata(Metadata):
    model_config = ConfigDict(validate_assignment=True)
    attributes: AttributesType = Field(default_factory=list)  # add default
    missions: list[Mission] = Field(default_factory=list, exclude=True)
    instruments: list[str] = Field(default_factory=list, exclude=True)
