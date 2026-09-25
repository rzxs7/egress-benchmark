from egress_bench.metrics import percentile, summarize
from egress_bench.models import RequestResult


def test_percentile_basic():
    assert percentile([10, 20, 30, 40], 0.5) == 25


def test_summary():
    rows = [
        RequestResult("baseline", 0, True, 200, 10),
        RequestResult("baseline", 1, False, 429, 30),
    ]
    s = summarize("baseline", rows)
    assert s.total == 2
    assert s.successes == 1
    assert s.success_rate == 0.5
    assert s.status_counts == {"200": 1, "429": 1}
