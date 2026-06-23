from aro.infrastructure.protection.memory_blocker import InMemoryBlocker
from aro.infrastructure.protection.nft_blocker import NftBlocker


def test_memory_blocker_block_unblock_list() -> None:
    b = InMemoryBlocker()
    b.block("203.0.113.5")
    b.block("203.0.113.6")
    assert b.list_blocked() == ["203.0.113.5", "203.0.113.6"]
    b.unblock("203.0.113.5")
    assert b.list_blocked() == ["203.0.113.6"]


class _FakeRunner:
    def __init__(self, table_missing: bool = False, set_output: str = "") -> None:
        self.calls: list[tuple[list[str], str | None]] = []
        self._table_missing = table_missing
        self._set_output = set_output

    def __call__(self, args: list[str], stdin: str | None = None) -> str:
        self.calls.append((args, stdin))
        if args[:2] == ["list", "table"]:
            if self._table_missing:
                raise RuntimeError("No such file or directory")
            return ""
        if args[:2] == ["list", "set"]:
            return self._set_output
        return ""


def test_nft_ensures_table_with_ssh_guard_when_missing() -> None:
    runner = _FakeRunner(table_missing=True)
    NftBlocker(runner=runner)
    load = next(c for c in runner.calls if c[0][:2] == ["-f", "-"])
    assert "tcp dport 22 accept" in (load[1] or "")
    assert "ip saddr @blocked drop" in (load[1] or "")


def test_nft_does_not_recreate_existing_table() -> None:
    runner = _FakeRunner(table_missing=False)
    NftBlocker(runner=runner)
    assert all(c[0][:2] != ["-f", "-"] for c in runner.calls)


def test_nft_block_and_unblock_commands() -> None:
    runner = _FakeRunner()
    b = NftBlocker(runner=runner)
    b.block("203.0.113.5")
    b.unblock("203.0.113.5")
    add = (["add", "element", "inet", "aro_ips", "blocked", "{ 203.0.113.5 }"], None)
    delete = (["delete", "element", "inet", "aro_ips", "blocked", "{ 203.0.113.5 }"], None)
    assert add in runner.calls
    assert delete in runner.calls


def test_nft_list_blocked_parses_elements() -> None:
    out = "table inet aro_ips {\n  set blocked {\n    elements = { 1.2.3.4, 5.6.7.8 }\n  }\n}"
    b = NftBlocker(runner=_FakeRunner(set_output=out))
    assert b.list_blocked() == ["1.2.3.4", "5.6.7.8"]


def test_nft_swallows_errors() -> None:
    class _Boom:
        def __call__(self, args: list[str], stdin: str | None = None) -> str:
            if args[:2] == ["list", "table"]:
                return ""
            raise RuntimeError("nft failure")

    b = NftBlocker(runner=_Boom())
    b.block("1.2.3.4")  # ne doit pas lever
    b.unblock("1.2.3.4")
    assert b.list_blocked() == []
