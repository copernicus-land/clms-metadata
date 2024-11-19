import abc
import datetime
from pathlib import Path
from typing import Annotated, Any, Literal

from cloudpathlib import CloudPath
from geojson_pydantic.geometries import Geometry
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.functional_serializers import PlainSerializer
from pydantic.functional_validators import AfterValidator

from clms_metadata.util import format_zulu


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


class StringAttribute(Attribute):
    value_type: Literal["String"] = "String"
    value: str


class IntegerAttribute(Attribute):
    value_type: Literal["Integer"] = "Integer"
    value: int


class DateTimeOffset(Attribute):
    value_type: Literal["DateTimeOffset"] = "DateTimeOffset"
    value: DateTimeUTC


MANDATORY_ATTRIBUTES = {
    "processingCenter": StringAttribute,
    "nominalDate": DateTimeOffset,
    "title": StringAttribute,
    # "tileId": StringAttribute,  # only if applicable
    # "relativeOrbitNumber": IntegerAttribute,
    # "productGroupId": StringAttribute,
    "productVersion": StringAttribute,
    # "resolution": IntegerAttribute,
}


def validate_attributes(attrs: list[Attribute]) -> list[Attribute]:
    for attribute, atype in MANDATORY_ATTRIBUTES.items():
        assert (
            len(filtered := [attr for attr in attrs if attr.name == attribute]) == 1
        ), f"Expected attribute with name '{attribute}'"
        assert isinstance(
            filtered[0], atype
        ), f"Expected '{attribute}' attribute with value type String"
    return attrs


Attributes = Annotated[
    list[
        Annotated[
            StringAttribute | IntegerAttribute | DateTimeOffset,
            Field(discriminator="value_type"),
        ]
    ],
    AfterValidator(validate_attributes),
]


class Metadata(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True, validate_assignment=True)

    name: str
    """Data file name"""

    content_type: str
    """The MIME type of the product"""

    content_length: int | None = Field(gt=0, default=None)
    """Actual size in bytes of the product"""

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

    checksum: str | None = None
    """MD5 checksum"""

    geometry: Geometry
    """Geometry of the geo-referenced product"""

    path: Path | CloudPath
    """Path of the product"""

    product_type: str
    """Product type"""

    dataset_name: str
    """Dataset name"""

    version: str
    """Product version"""

    attributes: Attributes

    @field_validator("geometry", mode="before")
    @classmethod
    def set_geometry(cls, geometry: Any) -> Any:
        """set geometry from geo interface or input"""
        if hasattr(geometry, "__geo_interface__"):
            return geometry.__geo_interface__
        return geometry
