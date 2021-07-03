from unittest import mock

from sql import add_to_db


class MagicMockContext(mock.MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        type(self).__aenter__ = mock.AsyncMock(return_value=mock.MagicMock())
        type(self).__aexit__ = mock.AsyncMock(return_value=mock.MagicMock())


async def test_add_to_db():
    conn = mock.AsyncMock(fetchrow=mock.AsyncMock(side_effect=[[mock.Mock(days=8)], [1]]), transaction=MagicMockContext())
    body = {
        "location1": {
            "lat": 56.7448873,
            "long": 49.1811542
            },
        "location2": {
            "lat": 55.74550,
            "long": 49.189232
          }
    }
    user_id, status = await add_to_db(conn, "2021-06-30 12:42:10.940759", body, 1)
    assert user_id['user_id'] == 1
    assert status == 201