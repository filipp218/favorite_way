from aiohttp import web
from sql import conn_to_db, add_to_db, get_from_db, check
from jsonschema import validate, exceptions
from shema import favorite_way_post, check_favorite_way

routes = web.RouteTableDef()


@routes.post('/favoriteway/{id}')
async def add_favoriteway(request):
    user_id = int(request.match_info['id'])
    body = await request.json()
    conn = await conn_to_db()

    try:
        validate(instance=body, schema=favorite_way_post)
    except exceptions.ValidationError:
        data = {'validation_error': {'user_id': user_id}}
        return web.Response(body=f'{data}', status=400)

    user_id, status = await add_to_db(conn, body, user_id)
    return web.Response(body=f'{user_id}', status=status)


@routes.get('/favoriteway/{id}')
async def add_favoriteway(request):
    user_id = request.match_info['id']
    conn = await conn_to_db()
    data, status = await get_from_db(conn, user_id)
    return web.Response(body=f'{data}', status=status)


@routes.post('/check')
async def check_favoriteway(request):
    body = await request.json()
    conn = await conn_to_db()
    try:
        validate(instance=body, schema=check_favorite_way)
    except exceptions.ValidationError:
        data = {'validation_error': 'Не валидные данные'}
        return web.Response(body=f'{data}', status=400)

    res = await check(conn, body)
    return web.Response(body=f'{res}', status=200)

app = web.Application()
app.add_routes(routes)
web.run_app(app)
