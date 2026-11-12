import base64

import aiohttp
import allure
import pytest


@allure.feature('Pet — питомцы')
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.asyncio
@pytest.mark.parametrize('negative', [False, True], ids=['positive', 'negative'])
class TestPet:
    @allure.story('POST /pet — создание питомца')
    @allure.title('Создание питомца: negative={negative}')
    async def test_create(self, client, pet_data, negative):
        data = dict(pet_data)
        if negative:
            data['id'] = 'not_an_integer'
        result = await client.request('POST', '/pet', body=data)
        assert result['status'] == (405 if negative else 200), result
        if not negative:
            assert result['body']['name'] == data['name']
            found = await client.request('GET', f'/pet/{data["id"]}')
            assert found['status'] == 200, found
            assert found['body']['name'] == data['name']

    @allure.story('PUT /pet — изменение питомца')
    @allure.title('Изменение питомца: negative={negative}')
    async def test_update(self, client, pet, negative):
        data = dict(pet)
        data['name'] += '_updated'
        if negative:
            data['id'] = 'not_an_integer'
        result = await client.request('PUT', '/pet', body=data)
        assert result['status'] == (400 if negative else 200), result
        if not negative:
            found = await client.request('GET', f'/pet/{pet["id"]}')
            assert found['status'] == 200, found
            assert found['body']['name'] == data['name']

    @allure.story('GET /pet/findByStatus — поиск по статусу')
    @allure.title('Поиск питомцев по статусу: negative={negative}')
    async def test_status(self, client, pet, negative):
        status = 'invalid_status' if negative else 'available'
        result = await client.request('GET', '/pet/findByStatus',
                                      params={'status': status})
        assert result['status'] == (400 if negative else 200), result
        if not negative:
            assert isinstance(result['body'], list)
            assert all(item['status'] == status for item in result['body'])
            assert any(item['id'] == pet['id'] for item in result['body'])

    @allure.story('GET /pet/findByTags — поиск по тегам')
    @allure.title('Поиск питомцев по тегам: negative={negative}')
    async def test_tags(self, client, pet, negative):
        params = {} if negative else {'tags': pet['tags'][0]['name']}
        result = await client.request('GET', '/pet/findByTags', params=params)
        assert result['status'] == (400 if negative else 200), result
        if not negative:
            assert isinstance(result['body'], list)
            assert any(item['id'] == pet['id'] for item in result['body'])

    @allure.story('GET /pet/{petId} — получение питомца')
    @allure.title('Получение питомца: negative={negative}')
    async def test_get(self, client, pet, negative):
        pet_id = 'not_an_integer' if negative else pet['id']
        result = await client.request('GET', f'/pet/{pet_id}')
        assert result['status'] == (400 if negative else 200), result
        if not negative:
            assert result['body']['id'] == pet['id']
            assert result['body']['name'] == pet['name']

    @allure.story('POST /pet/{petId} — изменение через форму')
    @allure.title('Изменение питомца через форму: negative={negative}')
    async def test_form(self, client, pet, negative):
        pet_id = 'not_an_integer' if negative else pet['id']
        result = await client.request('POST', f'/pet/{pet_id}',
                                      form={'name': pet['name'] + '_form',
                                            'status': 'sold'})
        assert result['status'] == (405 if negative else 200), result
        if not negative:
            found = await client.request('GET', f'/pet/{pet["id"]}')
            assert found['status'] == 200, found
            assert found['body']['status'] == 'sold'
            assert found['body']['name'] == pet['name'] + '_form'

    @allure.story('DELETE /pet/{petId} — удаление питомца')
    @allure.title('Удаление питомца: negative={negative}')
    async def test_delete(self, client, pet, negative):
        pet_id = 'not_an_integer' if negative else pet['id']
        result = await client.request('DELETE', f'/pet/{pet_id}')
        assert result['status'] == (400 if negative else 200), result
        if not negative:
            found = await client.request('GET', f'/pet/{pet["id"]}')
            assert found['status'] == 404, found

    @allure.story('POST /pet/{petId}/uploadImage — загрузка изображения')
    @allure.title('Загрузка изображения: negative={negative}')
    async def test_upload(self, client, pet, negative):
        pet_id = 'not_an_integer' if negative else pet['id']
        image = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aAt8AAAAASUVORK5CYII=')
        form = aiohttp.FormData()
        form.add_field('file', image, filename='kt6.png', content_type='image/png')
        result = await client.request('POST', f'/pet/{pet_id}/uploadImage', form=form)
        assert result['status'] == (400 if negative else 200), result
        if not negative:
            assert result['body']['code'] == 200
            assert 'kt6.png' in result['body']['message']
