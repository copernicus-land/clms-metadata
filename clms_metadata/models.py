import abc
import datetime
from pathlib import Path
from typing import Annotated, Literal, Optional

from cloudpathlib import CloudPath
from geojson_pydantic.geometries import Geometry
from pydantic import BaseModel, ConfigDict, Field
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


class Checksum(BaseModel):
    value: str
    algorithm: str
    checksum_date: DateTimeUTC


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


def validate_attributes(attrs: list[Attribute]) -> list[Attribute]:
    mandatory_string_attributes = ("processingCenter", "datasetIdentifier")
    for a_name in mandatory_string_attributes:
        assert (
            len(filtered := [attr for attr in attrs if attr.name == a_name]) == 1
        ), f"Expected attribute with name '{a_name}'"
        assert isinstance(
            filtered[0], StringAttribute
        ), f"Expected '{a_name}' attribute with value type String"
    return attrs


Attributes = Annotated[
    list[
        Annotated[StringAttribute | IntegerAttribute, Field(discriminator="value_type")]
    ],
    AfterValidator(validate_attributes),
]


class Metadata(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True)

    name: str
    """Data file name"""

    content_type: str
    """The MIME type of the product"""

    content_length: int = Field(gt=0)
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

    checksum: Optional[Checksum] = None

    content_date: ContentDate

    geometry: Geometry
    """Geometry of the geo-referenced product"""

    path: Path | CloudPath

    attributes: Attributes
