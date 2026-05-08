"""Unit tests for __version__.py."""

import diffpy.batchpdfsuite  # noqa


def test_package_version():
    """Ensure the package version is defined and not set to the initial
    placeholder."""
    assert hasattr(diffpy.batchpdfsuite, "__version__")
    assert diffpy.batchpdfsuite.__version__ != "0.0.0"
