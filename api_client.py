import json

import allure


class ApiClient:
    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url

    async def request(self, method, path, body=None, params=None, form=None,
                      api_key='special-key'):
        url = self.base_url + path
        headers = {'Accept': 'application/json', 'api_key': api_key}
        with allure.step(f'{method} {path}'):
            request_data = {'method': method, 'path': path, 'params': params,
                            'body': body, 'multipart': form is not None}
            allure.attach(json.dumps(request_data, ensure_ascii=False, indent=2),
                          'Запрос', allure.attachment_type.JSON)
            async with self.session.request(method, url, json=body, params=params,
                                            data=form, headers=headers) as response:
                text = await response.text()
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    data = text
                result = {'status': response.status, 'body': data,
                          'headers': dict(response.headers)}
                allure.attach(json.dumps(result, ensure_ascii=False, indent=2),
                              'Ответ', allure.attachment_type.JSON)
                return result
