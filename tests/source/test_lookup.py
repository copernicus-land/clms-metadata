import datetime

import pytest
from dateutil.relativedelta import relativedelta

from clms_metadata.models.metadata import ContentDate
from clms_metadata.source.lookup import (
    calculate_content_date,
    get_relativedelta,
    matches_temporal_grid,
)


@pytest.mark.parametrize(
    ("temporal_grid", "expected"),
    [
        ("daily", relativedelta(days=1)),
        ("10daily", relativedelta(days=10)),
        ("monthly", relativedelta(months=1)),
        ("yearly", relativedelta(years=1)),
        ("3yearly", relativedelta(years=3)),
    ],
)
def test_get_relativedelta(temporal_grid, expected):
    assert expected == get_relativedelta(temporal_grid)


@pytest.mark.parametrize(
    ("content_date", "temporal_grid", "expected"),
    [
        (  # content date delta is too long
            ContentDate(start="2022-08-02T00:00:00Z", end="2023-02-28T23:59:59Z"),
            relativedelta(days=10),
            False,
        ),
        (  # normal case
            ContentDate(start="2023-01-11T00:00:00Z", end="2023-01-20T23:59:59Z"),
            relativedelta(days=10),
            True,
        ),
        (  # special case for months with 31 days
            ContentDate(start="2024-03-21T00:00:00Z", end="2024-03-31T23:59:59Z"),
            relativedelta(days=10),
            True,
        ),
        (  # special case for February
            ContentDate(start="2023-02-21T00:00:00Z", end="2023-02-28T23:59:59Z"),
            relativedelta(days=10),
            True,
        ),
        (  # special case for February with leap day
            ContentDate(start="2024-02-21T00:00:00Z", end="2024-02-29T23:59:59Z"),
            relativedelta(days=10),
            True,
        ),
        (
            ContentDate(start="2024-04-01T00:00:00Z", end="2024-04-30T23:59:59Z"),
            relativedelta(months=1),
            True,
        ),
        (
            ContentDate(start="2021-01-01T00:00:00Z", end="2021-01-01T00:00:00Z"),
            relativedelta(years=1),
            False,
        ),
    ],
)
def test_matches_temporal_grid(
    content_date: ContentDate, temporal_grid: relativedelta, expected: bool
):
    assert expected == matches_temporal_grid(content_date, temporal_grid)


@pytest.mark.parametrize(
    ("nominal_date", "temporal_grid", "expected"),
    [
        (
            datetime.datetime(2023, 2, 10, tzinfo=datetime.timezone.utc),
            relativedelta(days=10),
            ContentDate(
                start="2023-02-01T00:00:00.000Z", end="2023-02-10T23:59:59.999999Z"
            ),
        ),
        (  # special case for February
            datetime.datetime(2023, 2, 28, tzinfo=datetime.timezone.utc),
            relativedelta(days=10),
            ContentDate(
                start="2023-02-21T00:00:00Z", end="2023-02-28T23:59:59.999999Z"
            ),
        ),
        (  # special case for February with leap day
            datetime.datetime(2024, 2, 21, tzinfo=datetime.timezone.utc),
            relativedelta(days=10),
            ContentDate(
                start="2024-02-21T00:00:00Z", end="2024-02-29T23:59:59.999999Z"
            ),
        ),
        (  # special case for months with 31 days, nominal date == end
            datetime.datetime(2024, 1, 31, tzinfo=datetime.timezone.utc),
            relativedelta(days=10),
            ContentDate(
                start="2024-01-21T00:00:00Z", end="2024-01-31T23:59:59.999999Z"
            ),
        ),
        (  # special case for months with 31 days, nominal date == start
            datetime.datetime(2024, 1, 21, tzinfo=datetime.timezone.utc),
            relativedelta(days=10),
            ContentDate(
                start="2024-01-21T00:00:00Z", end="2024-01-31T23:59:59.999999Z"
            ),
        ),
        (
            datetime.datetime(2024, 2, 1, tzinfo=datetime.timezone.utc),
            relativedelta(months=1),
            ContentDate(
                start="2024-02-01T00:00:00Z", end="2024-02-29T23:59:59.999999Z"
            ),
        ),
        (
            datetime.datetime(2023, 3, 31, tzinfo=datetime.timezone.utc),
            relativedelta(months=1),
            ContentDate(
                start="2023-03-01T00:00:00Z", end="2023-03-31T23:59:59.999999Z"
            ),
        ),
        (
            datetime.datetime(2024, 9, 30, tzinfo=datetime.timezone.utc),
            relativedelta(months=1),
            ContentDate(
                start="2024-09-01T00:00:00Z", end="2024-09-30T23:59:59.999999Z"
            ),
        ),
    ],
)
def test_calculate_content_date(
    nominal_date: datetime.datetime, temporal_grid: relativedelta, expected: ContentDate
):
    assert expected == calculate_content_date(nominal_date, temporal_grid)
