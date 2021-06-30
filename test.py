from web_api import make_app
import pytest
from shema import favorite_way_get
import jsonschema as jsonschema


@pytest.fixture
def cli(loop, test_client):
    return loop.run_until_complete(test_client(make_app))


async def test_favoriteway_get(cli):
    resp = await cli.get('favoriteway/1')
    assert resp.status == 200
    text = await resp.json()
    validator = jsonschema.Draft7Validator(favorite_way_get)
    assert validator.is_valid(text)


async def test_check_post(cli):
    resp = await cli.post(
        '/check',
        json={
            "user_id": 28,
            "location1": {
                "lat": 56.7448873,
                "long": 49.1811542
            },
            "location2": {
                "lat": 55.74550,
                "long": 49.189232
            }
        }
    )
    assert resp.status == 200
