import uuid

import aiohttp
import allure
import pytest
import pytest_asyncio

from api_client import ApiClient


@pytest_asyncio.fixture
async def client():
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout, trust_env=True) as session:
        yield ApiClient(session, 'https://petstore.swagger.io/v2')


@pytest_asyncio.fixture
async def pet_data(client):
    token = uuid.uuid4().hex[:12]
    data = {'id': int(token, 16), 'name': 'kt6_' + token,
            'photoUrls': [], 'tags': [{'id': 1, 'name': token}],
            'status': 'available'}
    yield data
    with allure.step('Убрать только своего тестового питомца'):
        found = await client.request('GET', f'/pet/{data["id"]}')
        assert found['status'] in (200, 404), found
        if found['status'] == 200:
            assert found['body'].get('id') == data['id'], 'Чужая запись: не удаляю'
            assert found['body'].get('tags') == data['tags'], 'Чужая запись: не удаляю'
            deleted = await client.request('DELETE', f'/pet/{data["id"]}')
            assert deleted['status'] in (200, 404), deleted
            found = await client.request('GET', f'/pet/{data["id"]}')
            assert found['status'] == 404, found


@pytest_asyncio.fixture
async def pet(client, pet_data):
    response = await client.request('POST', '/pet', body=pet_data)
    assert response['status'] == 200, response
    assert response['body']['id'] == pet_data['id']
    return pet_data


@pytest_asyncio.fixture
async def user_data(client):
    token = uuid.uuid4().hex[:12]
    data = {'id': int(token, 16), 'username': 'kt6_' + token,
            'firstName': 'Test', 'lastName': 'Student',
            'email': token + '@example.com', 'password': 'Kt6TestPassword',
            'phone': '1234567890', 'userStatus': 0}
    yield data
    with allure.step('Убрать только своего тестового пользователя'):
        found = await client.request('GET', f'/user/{data["username"]}')
        assert found['status'] in (200, 404), found
        if found['status'] == 200:
            assert found['body'].get('id') == data['id'], 'Чужая запись: не удаляю'
            assert found['body'].get('username') == data['username'], 'Чужая запись: не удаляю'
            deleted = await client.request('DELETE', f'/user/{data["username"]}')
            assert deleted['status'] in (200, 404), deleted
            found = await client.request('GET', f'/user/{data["username"]}')
            assert found['status'] == 404, found


@pytest_asyncio.fixture
async def user(client, user_data):
    response = await client.request('POST', '/user', body=user_data)
    assert response['status'] == 200, response
    return user_data


@pytest_asyncio.fixture
async def order_data(client, pet):
    free_id = None
    for order_id in range(1, 11):
        response = await client.request('GET', f'/store/order/{order_id}')
        if response['status'] == 404:
            free_id = order_id
            break
        assert response['status'] == 200, response
    if free_id is None:
        pytest.skip('Все ID заказов 1–10 заняты: чужие заказы не перезаписываем')
    data = {'id': free_id, 'petId': pet['id'], 'quantity': 2,
            'shipDate': '2026-11-12T12:00:00.000Z',
            'status': 'placed', 'complete': False}
    yield data
    with allure.step('Убрать заказ, только если он относится к нашему питомцу'):
        found = await client.request('GET', f'/store/order/{free_id}')
        assert found['status'] in (200, 404), found
        if found['status'] == 200:
            assert found['body'].get('id') == free_id, 'Чужая запись: не удаляю'
            assert found['body'].get('petId') == pet['id'], 'Чужая запись: не удаляю'
            deleted = await client.request('DELETE', f'/store/order/{free_id}')
            assert deleted['status'] in (200, 404), deleted
            found = await client.request('GET', f'/store/order/{free_id}')
            assert found['status'] == 404, found


@pytest_asyncio.fixture
async def order(client, order_data):
    response = await client.request('POST', '/store/order', body=order_data)
    assert response['status'] == 200, response
    assert response['body']['petId'] == order_data['petId']
    return order_data
