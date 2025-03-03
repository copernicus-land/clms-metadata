import datetime
from collections import OrderedDict
from copy import deepcopy
from typing import Any, Iterable, Optional, Tuple, Type

from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo


def format_zulu(date: datetime.datetime) -> str:
    """
    Format a datetime object as a zulu time string.
    :param date: the datetime object to format
    :return: the formatted datetime string
    """
    timespec = "microseconds"
    # timespec = "auto"
    # if date.microsecond:
    #     # prefer milliseconds if possible
    #     timespec = "milliseconds" if date.microsecond % 1000 == 0 else "microseconds"
    if date.tzinfo is None:
        return date.isoformat(timespec=timespec) + "Z"
    else:
        return date.isoformat(timespec=timespec).replace("+00:00", "Z")


def partial_model(model: Type[BaseModel]):
    """
    Partial Pydantic model decorator.

    https://stackoverflow.com/a/76560886/9339603

    :param model: Pydantic model class
    :return: partial model class
    """

    def make_field_optional(
        field: FieldInfo, default: Any = None
    ) -> Tuple[Any, FieldInfo]:
        new = deepcopy(field)
        new.default = default
        new.annotation = Optional[field.annotation]  # type: ignore
        return new.annotation, new

    return create_model(
        f"Partial{model.__name__}",
        __base__=model,
        __module__=model.__module__,
        **{
            field_name: make_field_optional(field_info)
            for field_name, field_info in model.model_fields.items()
        },
    )


def unique_list(list_in: Iterable) -> list:
    """
    Filter duplicate entries from a list while maintaining ordering.
    If None occurs in the list, it will be placed as the last element.

    :param list_in:
    :return:
    """
    list_dict = OrderedDict.fromkeys(list_in)
    if None in list_dict:
        list_dict.move_to_end(None)

    return list(list_dict.keys())
