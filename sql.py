from datetime import datetime
import asyncpg
import shapely.geometry
import shapely.wkb


async def conn_to_db():
    """
    Открываем соединение с БД и добавляем расширение для работы с типом geometry
    """
    conn = await asyncpg.connect("postgresql://127.0.0.1:5432/postgres")

    def encode_geometry(geometry):
        if not hasattr(geometry, '__geo_interface__'):
            raise TypeError('{g} does not conform to '
                            'the geo interface'.format(g=geometry))
        shape = shapely.geometry.asShape(geometry)
        return shapely.wkb.dumps(shape)

    def decode_geometry(wkb):
        return shapely.wkb.loads(wkb)

    await conn.set_type_codec(
        'geometry',  # также работает для 'geography'
        encoder=encode_geometry,
        decoder=decode_geometry,
        format='binary', )

    return conn


async def add_to_db(conn, body: dict, user_id: int) -> tuple:
    """
    Добавляем любимый маршрут пользователя в БД, если прошло больше 7 дней с предыдущей
    записи, деактивируем старую запись.
    """
    install_date = body['install_date']
    install_date = datetime.strptime(install_date, "%Y-%m-%d %H:%M:%S.%f")
    query = """
        SELECT $1::timestamp - install_date
        FROM Favorite_way
        WHERE user_id = $2 and is_active = True;
    """

    diff_date = await conn.fetchrow(query, install_date, user_id)  # узнаем, сколько дней прошло с прошлой записи

    if diff_date is not None:  # если diff_date возвращает None значит пользователь первый раз добавляет любимый маршрут
        if not diff_date[0].days >= 7:  # Можно обновлять любимую поездку только раз в 7 дней
            data = {'validation_error': {'user_id': user_id},
                    'error': 'Ещё не прошло 7 дней'}
            status = 400
            return data, status

    try:
        is_active = True
        a1, b1 = body['location1']['lat'], body['location1']['long']
        location1 = shapely.geometry.Point(b1, a1)
        a2, b2 = body['location2']['lat'], body['location2']['long']
        location2 = shapely.geometry.Point(b2, a2)

        query_deactivate = """
            UPDATE Favorite_way
            SET is_active = FALSE 
            WHERE user_id = $1 and is_active = TRUE;
            """

        query_add = """
            INSERT INTO Favorite_way
            (user_id, location1, location2, install_date, is_active)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING user_id
            """

        async with conn.transaction():
            await conn.execute(query_deactivate, user_id)
            user_id = await conn.fetchrow(query_add, user_id, location1, location2, install_date, is_active)
    finally:
        await conn.close()
    status = 201

    return {'user_id': user_id[0]}, status


async def check(conn, body: dict) -> dict:
    """
    Проверяем является ли выбранный маршрут пользователем его любимым.
    В переменной over_range хранится максимальное расстояние, на котором пользователь
    может находиться от точек заданных в его любимом маршруте
    """

    user_id = body['user_id']
    a1, b1 = body['location1']['lat'], body['location1']['long'],
    origin = shapely.geometry.Point(b1, a1)
    a2, b2 = body['location2']['lat'], body['location2']['long'],
    destination = shapely.geometry.Point(b2, a2)

    query = """
        SELECT (ST_DistanceSphere($1, location1) < $4 and 
        ST_DistanceSphere ($2, location2) < $4) or
        (ST_DistanceSphere ($1, location2) < $4 and
        ST_DistanceSphere (location1, $2) < $4)
        FROM Favorite_way
        WHERE user_id = $3 and is_active is TRUE;
    """
    over_range = 100  # расстояние в метрах
    res = await conn.fetchrow(query, origin, destination, user_id, over_range)
    await conn.close()
    if res:  # если запись о любимой поездки юзера есть и получилось сравнить
        return {
            'user_id': user_id,
            'location1': body['location1'],
            'location2': body['location2'],
            'favorite_way': res[0]}

    res = {'user_id': user_id,
           'location1': body['location1'],
           'location2': body['location2'],
           'favorite_way': False}
    return res


async def get_from_db(conn, user_id: int) -> tuple:
    """
    Получаем из БД любимый маршрут пользователя
    """
    query = """
        SELECT user_id, 
                (ST_X(location1), ST_Y(location1)), 
                (ST_X(location1), ST_Y(location2)), 
                install_date
        FROM Favorite_way
        WHERE user_id = $1 and is_active is TRUE;
    """

    data = await conn.fetchrow(query, int(user_id))
    if not data:
        data = {'validation_error': {
            'user_id': user_id,
            'favorite_way': False},
            'error': 'Пользователь ещё не выбрал любимый маршрут'}
        status = 400
        return data, status
    long1, lat1 = data[1]
    long2, lat2 = data[2]
    data = {'user_id': data[0],
            'location1': {'lat': lat1, 'long': long1},
            'location2': {'lat': lat2, 'long': long2},
            'install_date': str(data[3])}
    await conn.close()
    status = 200
    return data, status
