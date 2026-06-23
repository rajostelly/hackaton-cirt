from aro.domain.virus.entities import VirusReport


def test_score_and_is_malicious() -> None:
    r = VirusReport("1.2.3.4", "ip", malicious=10, suspicious=0, harmless=40, total=50)
    assert r.score == 0.2
    assert r.is_malicious is True


def test_clean_report() -> None:
    r = VirusReport("1.2.3.4", "ip", malicious=0, suspicious=0, harmless=50, total=50)
    assert r.score == 0.0
    assert r.is_malicious is False


def test_zero_total_score() -> None:
    r = VirusReport("x", "file", 0, 0, 0, 0)
    assert r.score == 0.0
