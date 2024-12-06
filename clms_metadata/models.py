import abc
import datetime
from pathlib import Path
from typing import Annotated, Any, Literal, Type

from cloudpathlib import CloudPath
from geojson_pydantic.geometries import Geometry
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.functional_serializers import PlainSerializer
from pydantic.functional_validators import AfterValidator

from clms_metadata.constants import attributes
from clms_metadata.util import format_zulu, partial_model


def validate_utc(d: datetime.datetime) -> datetime.datetime:
    """
    Validate if the provided datetime is in UTC.

    :param d: datetime to validate
    :return: datetime
    """
    assert d.tzinfo == datetime.timezone.utc, "Expected datetime in UTC, got {}".format(
        d
    )
    return d


DateTimeUTC = Annotated[
    datetime.datetime, AfterValidator(validate_utc), PlainSerializer(format_zulu)
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
    value: str


class IntegerAttribute(Attribute):
    value_type: Literal["Integer"] = "Integer"
    value: int


class DateTimeOffsetAttribute(Attribute):
    value_type: Literal["DateTimeOffset"] = "DateTimeOffset"
    value: DateTimeUTC


MANDATORY_ATTRIBUTES = {
    attributes.PROCESSING_CENTER: StringAttribute,
    attributes.NOMINAL_DATE: DateTimeOffsetAttribute,
    attributes.DATASET_IDENTIFIER: StringAttribute,
    attributes.DATASET_SHORT_NAME: StringAttribute,
    attributes.DATASET_ALIAS: StringAttribute,
    attributes.COLLECTION_VERSION: IntegerAttribute,
    attributes.COMPONENT: StringAttribute,  # TODO: to be moved to main properties?
    attributes.FILE_FORMAT: StringAttribute,
    attributes.TEMPORAL_GRID: StringAttribute,
    "productVersion": StringAttribute,  # TODO: should this be kept?
    attributes.NOMINAL_RESOLUTION_METERS: IntegerAttribute,
    attributes.NOMINAL_RESOLUTION: StringAttribute,
    attributes.SPATIAL_EXTENT: StringAttribute,
}

OPTIONAL_ATTRIBUTES = {
    # only checked to have the following type when they are present
    "tileId": StringAttribute,
    "relativeOrbitNumber": IntegerAttribute,
    "productGroupId": StringAttribute,  # TODO: still relevant?
    attributes.CONSOLIDATION_PERIOD: IntegerAttribute,
    attributes.SEASON: StringAttribute,
    attributes.PRODUCT_VARIABLE: StringAttribute,
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


Attributes = Annotated[
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

    name_suffix: str
    """Product name suffix"""

    content_type: str
    """The MIME type of the product"""

    origin_date: DateTimeUTC
    """Date and time of the product at the source in UTC"""

    publication_date: DateTimeUTC = Field(
        default_factory=lambda: datetime.datetime.now(tz=datetime.timezone.utc)
    )
    """Publication date and time of the product in UTC"""

    modification_date: DateTimeUTC = Field(
        default_factory=lambda: datetime.datetime.now(tz=datetime.timezone.utc)
    )
    """Date and time when the product metadata was last modified in UTC"""

    content_date: ContentDate
    """Sensing range period"""

    geometry: Geometry
    """Geometry of the geo-referenced product"""

    path: Path | CloudPath
    """Path of the product"""

    product_type: str
    """Product type"""

    attributes: Attributes

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
        return next(a for a in self.attributes if a.name == name)

    def add_attribute(self, name: str, value_type: Type[Attribute], factory: callable):
        """
        Add an attribute to the attribute list in the metadata.

        :param name: attribute name
        :param value_type: type of the attribute value
        :param factory: method to extract the attribute value
        :return:
        """
        if not self.has_attribute(name):
            value = factory()
            if value is not None:
                self.attributes.append(value_type(name=name, value=value))


@partial_model
class PartialMetadata(Metadata):
    model_config = ConfigDict(validate_assignment=True)
    attributes: Attributes = Field(default_factory=list)  # add default
