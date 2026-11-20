from app.services.liveboard import _clear, _copy, _store, load_live_board
from app.services.prometheus import IntegrationStatus


def test_cached_board_is_an_isolated_copy():
    try:
        _store({"availability": "1%"}, [{"name": "WEB01", "status": "Healthy"}], IntegrationStatus(True, "ok"))
        first = _copy()
        first[1][0]["status"] = "Unreachable"
        second = _copy()
        assert second[1][0]["status"] == "Healthy"
    finally:
        _clear()


def test_testing_ignores_the_live_cache(seeded):
    try:
        _store({"availability": "cached"}, [{"name": "CACHED"}], IntegrationStatus(False, "cached"))
        with seeded.app_context():
            _metrics, hosts, _status, cached = load_live_board()
        assert cached is False
        assert hosts[0]["name"] != "CACHED"
    finally:
        _clear()
