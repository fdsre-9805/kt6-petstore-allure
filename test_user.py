import allure
import pytest


@allure.feature('User — пользователи')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.asyncio
@pytest.mark.parametrize('negative', [False, True], ids=['positive', 'negative'])
class TestUser:
    @allure.story('POST /user — создание пользователя')
    @allure.title('Создание пользователя: negative={negative}')
    async def test_create(self, client, user_data, negative):
        data = dict(user_data)
        if negative:
            data['id'] = 'not_an_integer'
        result = await client.request('POST', '/user', body=data)
        assert result['status'] == (400 if negative else 200), result
        if not negative:
            found = await client.request('GET', f'/user/{data["username"]}')
            assert found['status'] == 200, found
            assert found['body']['email'] == data['email']

    @allure.story('POST /user/createWithList — создание списка пользователей')
    @allure.title('Создание списка пользователей: negative={negative}')
    async def test_list(self, client, user_data, negative):
        data = dict(user_data)
        if negative:
            data['id'] = 'not_an_integer'
        result = await client.request('POST', '/user/createWithList', body=[data])
        assert result['status'] == (400 if negative else 200), result
        if not negative:
            found = await client.request('GET', f'/user/{data["username"]}')
            assert found['status'] == 200, found
            assert found['body']['id'] == data['id']

    @allure.story('POST /user/createWithArray — создание массива пользователей')
    @allure.title('Создание массива пользователей: negative={negative}')
    async def test_array(self, client, user_data, negative):
        data = dict(user_data)
        if negative:
            data['id'] = 'not_an_integer'
        result = await client.request('POST', '/user/createWithArray', body=[data])
        assert result['status'] == (400 if negative else 200), result
        if not negative:
            found = await client.request('GET', f'/user/{data["username"]}')
            assert found['status'] == 200, found
            assert found['body']['id'] == data['id']

    @allure.story('GET /user/{username} — получение пользователя')
    @allure.title('Получение пользователя: negative={negative}')
    async def test_get(self, client, user, negative):
        username = user['username'] + '_missing' if negative else user['username']
        result = await client.request('GET', f'/user/{username}')
        assert result['status'] == (404 if negative else 200), result
        if not negative:
            assert result['body']['id'] == user['id']
            assert result['body']['email'] == user['email']

    @allure.story('PUT /user/{username} — изменение пользователя')
    @allure.title('Изменение пользователя: negative={negative}')
    async def test_update(self, client, user, negative):
        data = dict(user)
        data['email'] = 'updated@example.com'
        if negative:
            data['id'] = 'not_an_integer'
        result = await client.request('PUT', f'/user/{user["username"]}', body=data)
        assert result['status'] == (400 if negative else 200), result
        if not negative:
            found = await client.request('GET', f'/user/{user["username"]}')
            assert found['status'] == 200, found
            assert found['body']['email'] == data['email']

    @allure.story('DELETE /user/{username} — удаление пользователя')
    @allure.title('Удаление пользователя: negative={negative}')
    async def test_delete(self, client, user, negative):
        username = user['username'] + '_missing' if negative else user['username']
        result = await client.request('DELETE', f'/user/{username}')
        assert result['status'] == (404 if negative else 200), result
        if not negative:
            found = await client.request('GET', f'/user/{user["username"]}')
            assert found['status'] == 404, found

    @allure.story('GET /user/login — вход')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('Вход пользователя: negative={negative}')
    async def test_login(self, client, user, negative):
        password = 'wrong_password' if negative else user['password']
        result = await client.request('GET', '/user/login',
                                      params={'username': user['username'],
                                              'password': password})
        assert result['status'] == (400 if negative else 200), result
        if not negative:
            assert 'logged in' in result['body']['message'].lower()

    @allure.story('GET /user/logout — выход')
    @allure.title('Выход пользователя: negative={negative}')
    async def test_logout(self, client, negative):
        method = 'PATCH' if negative else 'GET'
        result = await client.request(method, '/user/logout')
        assert result['status'] == (405 if negative else 200), result
        if not negative:
            assert result['body']['code'] == 200
