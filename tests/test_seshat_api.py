import pytest
from pytest import raises
import requests
from seshat_api import (
    SeshatAPI,
    get_variable_classes,
    get_variable_name,
    seshat_class_instance,
    get_frequencies,
)
from seshat_api.base_model import _Paginated
from seshat_api.constants import BASE_URL


def test_get_variable_name():
    assert get_variable_name("Camels") == "camel"
    assert get_variable_name("ExampleClasses") == "example_class"
    assert get_variable_name("BigPonies") == "big_pony"
    assert get_variable_name("AlreadySingular") == "already_singular"
    assert get_variable_name("Judges") == "judge"


def test_seshat_class_instance():
    # Assert this does not raise an error
    seshat_class_instance("ProfessionalSoldiers", "professional_soldier")
    
    # Assert this raises an ImportError
    with raises(ImportError):
        seshat_class_instance("FakeClasses", "fake_class")


def test_get_variable_classes():
    vc = get_variable_classes()
    assert "Coppers" in vc["wf"]
    assert "Roads" in vc["sc"]
    assert "PolitySuprapolities" in vc["general"]
    assert "Polities" in vc["core"]
    assert "ExternalConflictSides" in vc["crisisdb"]
    assert "OfficialReligions" in vc["rt"]
    assert "BigPonies" not in vc["wf"]


def test_paginated_iteration_no_duplicates():
    class DummyClient:
        def __init__(self):
            self.calls = []

        def get(self, url, params):
            self.calls.append(url)
            if url == "/items":
                return {
                    "next": f"{BASE_URL}/items?page=2",
                    "previous": None,
                    "results": [{"id": 1}, {"id": 2}],
                }
            if url == "/items?page=2":
                return {
                    "next": None,
                    "previous": f"{BASE_URL}/items",
                    "results": [{"id": 3}],
                }
            raise AssertionError(f"Unexpected url {url}")

    client = DummyClient()
    pager = _Paginated(client, "/items")
    ids = [item.id for item in pager]

    assert ids == [1, 2, 3]
    # Ensure only the two expected pages were fetched
    assert client.calls == ["/items", "/items?page=2"]
    # After iteration the pager should have no leftover results
    assert pager.results == []


# TODO: Use mocking instead of relying on the API
def test_get_frequencies():
    # Only run this test if we can access the API url
    base_url = "https://seshatdata.com/api"
    # base_url = "https://seshat-db.com/api"
    try:
        response = requests.get(base_url)
        response.raise_for_status()
    except requests.RequestException:
        pytest.skip(f"Cannot access {base_url}")

    client = SeshatAPI(base_url=base_url)
    class_names = ['Roads', 'ProfessionalSoldiers']
    years = range(0, 10)
    value = 'absent'
    df = get_frequencies(client, class_names, years, value)
    # Assert the df has 10 rows and 2 columns
    assert df.shape == (10, 2)
