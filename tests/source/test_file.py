import pytest

from clms_metadata.source.file import get_platform


@pytest.mark.parametrize(
    ("platformstr", "expected"),
    [
        ("Proba-V", {"PROBA-V": None}),
        ("SPOT-4", {"SPOT-4": None}),
        ("METOP A+B", {"METOP": ["A", "B"]}),
        ("Sentinel-1 A+B", {"SENTINEL-1": ["A", "B"]}),
        ("Sentinel-3A", {"SENTINEL-3": ["A"]}),
        ("METOP A+B, Sentinel-1 A+B", {"METOP": ["A", "B"], "SENTINEL-1": ["A", "B"]}),
        ("SENTINEL-3A AND SENTINEL-3B", {"SENTINEL-3": ["A", "B"]}),
        ("SENTINEL3A AND SENTINEL3B", {"SENTINEL-3": ["A", "B"]}),
        ("TERRA (EOS AM-1)", {"TERRA": None}),
        ("NOAA-20 (JPSS-1)", {"NOAA-20": None}),
    ],
)
def test_get_platform(platformstr, expected):
    # examples:
    # Proba-V => [PROBA-V]
    # SPOT 4 => [SPOT-4]
    # METOP A+B => [METOP-A, METOP-B]
    # Sentinel-1 A+B => [SENTINEL-1A, SENTINEL-1B]
    # METOP A+B, Sentinel-1 A+B => [METOP-A, METOP-B, SENTINEL-1A, SENTINEL-1B]
    # SENTINEL-3A AND SENTINEL-3B => [SENTINEL-3A, SENTINEL-3B]
    # SENTINEL3A AND SENTINEL3B => [SENTINEL-3A, SENTINEL-3B]
    # SENTINEL 3 (A AND B) => [SENTINEL-3A, SENTINEL-3B]
    # TERRA (EOS AM-1) => [TERRA]
    # NOAA-20 (JPSS-1) => [NOAA-20]
    assert get_platform({"platform": platformstr}) == expected
