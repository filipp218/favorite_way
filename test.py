import jsonschema as jsonschema

import pytest

from shema import check_favorite_way200, favorite_way_get, \
    favorite_way_get400, favorite_way_post201, favorite_way_post400

from sql import conn_to_db

from web_api import make_app


@pytest.fixture
def cli(loop, test_client):
    return loop.run_until_complete(test_client(make_app))


async def db():
    conn = await conn_to_db()
    await conn.execute("""
        DELETE FROM Favorite_way
        WHERE user_id = 100;
        """)
    await conn.close()


async def test_post_favoriteway(cli):
    resp = await cli.post(
        '/favoriteway/100',
        json={
            "location1": {
                "lat": 56.7448873,
                "long": 49.1811542
            },
            "location2": {
                "lat": 55.74550,
                "long": 49.189232
            },
            "install_date": "2021-06-30 12:42:10.940759"
        }
    )
    assert resp.status == 201
    text = await resp.json()
    validator = jsonschema.Draft7Validator(favorite_way_post201)
    assert validator.is_valid(text)


async def test_badpost_favoriteway(cli):
    resp = await cli.post(
        '/favoriteway/100',
        json={
            "location1": {
                "lat": 56.7448873,
                "long": 49.1811542
            },
            "location2": {
                "lat": 55.74550,
                "long": 49.189232
            },
            "install_date": "2021-06-30 12:42:10.940759"
        }
    )
    assert resp.status == 400
    text = await resp.json()
    validator = jsonschema.Draft7Validator(favorite_way_post400)
    assert validator.is_valid(text)


async def test_favoriteway_get(cli):
    resp = await cli.get('favoriteway/100')
    assert resp.status == 200
    text = await resp.json()
    validator = jsonschema.Draft7Validator(favorite_way_get)
    assert validator.is_valid(text)


async def test_favoriteway_badget(cli):
    resp = await cli.get('favoriteway/101')
    assert resp.status == 400
    text = await resp.json()
    validator = jsonschema.Draft7Validator(favorite_way_get400)
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
    await db()
    assert resp.status == 200
    text = await resp.json()
    validator = jsonschema.Draft7Validator(check_favorite_way200)
    assert validator.is_valid(text)


async def test_badcheck_post(cli):
    resp = await cli.post(
        '/check',
        json={
            "user_id": 28,
            "location1": {
                "lat": 56.7448873,
                "long": 49.1811542
            },
            "location2": {
                "lat": 55.74550
            }
        }
    )
    assert resp.status == 400
    text = await resp.json()
    answer = {"validation_error": "Не валидные данные"}
    await db()
    assert text == answer
