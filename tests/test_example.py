import pytest


def add(a, b):
    """Add two numbers."""
    return a + b


class TestSimpleFunctions:
    """Test class for simple add function as template example."""
    @pytest.mark.parametrize("a, b, expect", [(10, 5, 15), (20, 10, 30)])
    def test_add(self, a, b, expect):
        """Test add function."""
        assert add(a, b) == expect
