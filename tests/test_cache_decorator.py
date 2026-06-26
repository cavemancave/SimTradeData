"""Tests for @cached decorator."""

import pytest

from simtradedata.cache.decorator import DEFAULT_TTL, cached


@pytest.mark.unit
class TestCachedDecorator:
    """Tests for the @cached decorator."""

    def test_caches_return_value(self):
        call_count = 0

        @cached(ttl=60, key_prefix="test")
        def expensive():
            nonlocal call_count
            call_count += 1
            return 42

        assert expensive() == 42
        assert expensive() == 42
        assert call_count == 1

    def test_different_args_different_keys(self):
        @cached(ttl=60, key_prefix="add")
        def add(a, b):
            return a + b

        assert add(1, 2) == 3
        assert add(3, 4) == 7

    def test_same_args_cached(self):
        call_count = 0

        @cached(ttl=60, key_prefix="sq")
        def square(n):
            nonlocal call_count
            call_count += 1
            return n * n

        assert square(5) == 25
        assert square(5) == 25
        assert call_count == 1

    def test_invalidate(self):
        call_count = 0

        @cached(ttl=60, key_prefix="inv")
        def fetch():
            nonlocal call_count
            call_count += 1
            return call_count

        assert fetch() == 1
        fetch.invalidate()
        assert fetch() == 2

    def test_invalidate_with_args(self):
        @cached(ttl=60, key_prefix="inv_args")
        def get(key):
            return key.upper()

        assert get("a") == "A"
        get.invalidate("a")
        assert get("a") == "A"

    def test_nocache(self):
        call_count = 0

        @cached(ttl=60, key_prefix="nc")
        def counter():
            nonlocal call_count
            call_count += 1
            return call_count

        assert counter() == 1
        assert counter.nocache() == 2
        assert counter() == 1  # cache still has old value

    def test_works_with_kwargs(self):
        @cached(ttl=60, key_prefix="kw")
        def greet(name, greeting="hello"):
            return f"{greeting} {name}"

        assert greet("world") == "hello world"
        assert greet("world", greeting="hi") == "hi world"

    def test_works_as_method(self):
        class MyClass:
            def __init__(self):
                self.calls = 0

            @cached(ttl=60, key_prefix="method")
            def compute(self, x):
                self.calls += 1
                return x * 2

        obj = MyClass()
        assert obj.compute(5) == 10
        assert obj.compute(5) == 10
        assert obj.calls == 1


@pytest.mark.unit
class TestDefaultTTL:
    """Tests for the TTL configuration."""

    def test_stock_list_ttl_is_24h(self):
        assert DEFAULT_TTL["stock_list"] == 86400

    def test_trade_calendar_ttl_is_7d(self):
        assert DEFAULT_TTL["trade_calendar"] == 604800

    def test_snapshot_ttl_is_5s(self):
        assert DEFAULT_TTL["snapshot"] == 5
