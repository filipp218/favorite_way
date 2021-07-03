import random
from datetime import datetime

import jsonschema as jsonschema

import pytest

import shapely.geometry
import shapely.wkb

from shema import check_favorite_way200, favorite_way_get, \
    favorite_way_get400, favorite_way_post201, favorite_way_post400

from sql import conn_to_db

from web_api import make_app


@pytest.fixture
def cli(loop, test_client):
    return loop.run_until_complete(test_client(make_app))


@pytest.fixture
async def connection():
    conn = await conn_to_db()
    yield conn
    await conn.close()


@pytest.fixture
async def user_post(connection):
    user_id = random.randint(102, 1000)
    yield user_id
    await connection.execute(f"""
        DELETE FROM Favorite_way
        WHERE user_id = {user_id};
        """)


@pytest.fixture
async def user(connection):
    user_id = random.randint(102, 1000)
    query_add = """
        INSERT INTO Favorite_way(
            user_id, 
            location1, 
            location2, 
            install_date, 
            is_active
            )
        VALUES ($1, $2, $3, $4, $5)
        """
    a1, b1 = (56.7448873, 49.1811542)
    a2, b2 = (55.7455, 49.189232)
    location1 = shapely.geometry.Point(b1, a1)
    location2 = shapely.geometry.Point(b2, a2)
    date = datetime.now()
    await connection.execute(
        query_add,
        user_id,
        location1,
        location2,
        date,
        True)
    yield user_id
    await connection.execute(f"""
        DELETE FROM Favorite_way
        WHERE user_id = {user_id};
        """)


async def test_post_favoriteway(cli, user_post):
    body = {
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
    resp = await cli.post(f'/favoriteway/{user_post}', json=body)
    assert resp.status == 201
    text = await resp.json()
    validator = jsonschema.Draft7Validator(favorite_way_post201)
    assert validator.is_valid(text)

    resp = await cli.post(f'/favoriteway/{user_post}', json=body)
    assert resp.status == 400
    text = await resp.json()
    validator = jsonschema.Draft7Validator(favorite_way_post400)
    assert validator.is_valid(text)


async def test_badpost_favoriteway(cli):
    user = random.randint(1, 100)
    body = {
            "location1": {
                "lat": 56.7448873,
                "long": 49.1811542
            },
            "location2": {
                "lat": 55.74550,
            },
            "install_date": "2021-06-30 12:42:10.940759"
        }
    resp = await cli.post(f'/favoriteway/{user}', json=body)
    assert resp.status == 400
    text = await resp.json()
    validator = jsonschema.Draft7Validator(favorite_way_post400)
    assert validator.is_valid(text)


async def test_favoriteway_get(cli, user):
    resp = await cli.get(f'favoriteway/{user}')
    assert resp.status == 200
    text = await resp.json()
    validator = jsonschema.Draft7Validator(favorite_way_get)
    assert validator.is_valid(text)


async def test_favoriteway_badget(cli, user):
    not_real_user = user + 1
    resp = await cli.get(f'favoriteway/{not_real_user}')
    assert resp.status == 400
    text = await resp.json()
    validator = jsonschema.Draft7Validator(favorite_way_get400)
    assert validator.is_valid(text)


async def test_check_post_cool_distance(cli, user):
    resp = await cli.post(
        '/check',
        json={
            "user_id": user,
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
    text = await resp.json()
    assert text["favorite_way"] is True
    validator = jsonschema.Draft7Validator(check_favorite_way200)
    assert validator.is_valid(text)


async def test_check_post_bad_distance(cli, user):
    resp = await cli.post(
        '/check',
        json={
            "user_id": user,
            "location1": {
                "lat": 56.7448873,
                "long": 49.1811542
            },
            "location2": {
                "lat": 55.74550,
                "long": 60.189232
            }
        }
    )
    assert resp.status == 200
    text = await resp.json()
    assert text["favorite_way"] is False
    validator = jsonschema.Draft7Validator(check_favorite_way200)
    assert validator.is_valid(text)


async def test_badcheck_post(cli, user):
    resp = await cli.post(
        '/check',
        json={
            "user_id": user,
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
    assert text == answer
