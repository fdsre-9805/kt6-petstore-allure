import allure
import pytest


@allure.feature('Store — магазин')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.asyncio
@pytest.mark.parametrize('negative', [False, True], ids=['positive', 'negative'])
class TestStore:
    @allure.story('GET /store/inventory — остатки на складе')
    @allure.title('Остатки склада: negative={negative}')
    async def test_inventory(self, client, negative):
        key = 'invalid-key' if negative else 'special-key'
        result = await client.request('GET', '/store/inventory', api_key=key)
        if negative:
            assert result['status'] in (401, 403), result
        else:
            assert result['status'] == 200, result
            assert isinstance(result['body'], dict)
            assert all(isinstance(count, int) and count >= 0
                       for count in result['body'].values())

    @allure.story('POST /store/order — создание заказа')
    @allure.title('Создание заказа: negative={negative}')
    async def test_create(self, client, order_data, negative):
        data = dict(order_data)
        if negative:
            data['id'] = 'not_an_integer'
        result = await client.request('POST', '/store/order', body=data)
        assert result['status'] == (400 if negative else 200), result
        if not negative:
            assert result['body']['quantity'] == data['quantity']
            found = await client.request('GET', f'/store/order/{data["id"]}')
            assert found['status'] == 200, found
            assert found['body']['petId'] == data['petId']

    @allure.story('GET /store/order/{orderId} — получение заказа')
    @allure.title('Получение заказа: negative={negative}')
    async def test_get(self, client, order, negative):
        order_id = 'not_an_integer' if negative else order['id']
        result = await client.request('GET', f'/store/order/{order_id}')
        assert result['status'] == (400 if negative else 200), result
        if not negative:
            assert result['body']['id'] == order['id']
            assert result['body']['petId'] == order['petId']

    @allure.story('DELETE /store/order/{orderId} — удаление заказа')
    @allure.title('Удаление заказа: negative={negative}')
    async def test_delete(self, client, order, negative):
        order_id = 'not_an_integer' if negative else order['id']
        result = await client.request('DELETE', f'/store/order/{order_id}')
        assert result['status'] == (400 if negative else 200), result
        if not negative:
            found = await client.request('GET', f'/store/order/{order["id"]}')
            assert found['status'] == 404, found
