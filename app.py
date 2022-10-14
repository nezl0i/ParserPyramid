import logging
import sys
import requests
from requests.auth import AuthBase
import conf
import common.logs
from common.log_decorator import log
from common.headers import header, login_url, base_url, count_url, login_body, locate, instance_body, \
    instance_url, reports_url, create_report_url, delete_body, delete_url, access_level_url, configurator_url
from requests.exceptions import ConnectionError

LOGGER = logging.getLogger('parser')

items = {
    "Абоненты": -2147483648,
    "Физические лица": -1594,
    "Юридические лица": -1596,
    "Организация": -2147483647,
    "Подразделения": -29485,
    "Контрагенты": -29475,
    "Оборудование": -2147483646,
    "Внешние дисплеи": -9952,
    "Измерительные трансформаторы": -1576,
    "Каналообразующее оборудование": -1568,
    "Приборы учета электроэнергии": -1646,
    "Ресурсы каналообразования": -2147483645,
    "COM-порты": -1538,
    "Модемы": -1524,
    "Пулы модемов": -7847,
    "Серверные сокеты": -29076,
    "Сотовая связь": -2147483644,
    "SIM-карты": -8053,
    "Операторы сотовой связи": -8055,
    "Профили": -2147483643,
    "Профили источников данных": -3732,
    "Профили получения": -3798,
    "Профили отправки": -3796,
    "Профили дисплеев": -9960,
    "Технические учеты": 868770,
    "Пользовательские справочники": -8083}


class SessionUrlBase(requests.Session):
    def __init__(self, url_base=None):
        super(SessionUrlBase, self).__init__()
        self.url_base = url_base

    def request(self, method, url, **kwargs):
        modified_url = self.url_base + url

        return super(SessionUrlBase, self).request(method, modified_url, **kwargs)


class APIAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        # header['authorization'] = f'Bearer {self.api_token}'
        header['authorization'] = self.token
        r.headers.update(header)
        return r


class PyramidParser:

    def __init__(self):
        self.session = SessionUrlBase(url_base=base_url)
        self.session.headers.update(header)
        self.token = None
        self.route_id = []
        self.password = conf.PASSWD
        self.username = conf.LOGIN
        self.status = False
        self.item_count = 0
        self.login()
        LOGGER.info(f'Создан пользователь {self.username}')

    @log
    def login(self):
        login_body['username'] = self.username
        login_body['password'] = self.password
        try:
            out = self.session.post(login_url, json=login_body)
        except ConnectionError:
            print(f'Соединение не установлено.')
            LOGGER.critical(f'Соединение с сервером не установлено.')
            sys.exit(1)
        if out.status_code == 200:
            self.token = f"Bearer {out.json().get('tokens').get('accessToken')}"
            header['authorization'] = self.token
            self.session.headers.update(header)
            # self.session.auth = APIAuth(self.token)
            self.status = True

            print(f'Авторизация прошла успешно. Ответ сервера - {out}')
            LOGGER.info(f'Пользователь {self.username} успешно авторизовался. Ответ сервера - {out}')
        else:
            print(f'Неверное имя пользователя или пароль. Ответ сервера - {out}')
            LOGGER.error(f'Ошибка авторизации пользователя {self.username}. Ответ сервера - {out}')
            sys.exit(1)
        return out

    @log
    def count_instance(self, class_id):
        if self.status:
            instance_body['classId'] = class_id
            out = self.session.post(count_url, timeout=10, json=instance_body)
            self.item_count = out.json()
            print(f'Всего записей  - {self.item_count}')
            return out

    @log
    def count_branch_instance(self, class_id):
        total = 0
        instance_body['classId'] = class_id
        if self.status:
            for key, value in locate.items():
                instance_body['options']['take'] = '50'
                instance_body['options']['sort'] = '[{"selector":"id","desc":false}]'
                instance_body['options']['filter'] = f'["-13295", "contains", "{value}"]'

                count = self.session.post(count_url, json=instance_body)

                print(f'{key}: {count.text} ПУ')

                total += int(count.text)
            print(f'Всего ПУ в разрезе филиалов: {total}')
        return

    @log
    def instance_route(self, class_id):
        take = 1000  # Количество записей на странице
        skip = 0  # От какой записи
        instance_body['classId'] = class_id
        while skip < self.item_count - (self.item_count % 1000):
            instance_body['options']['sort'] = '[{"selector":"id","desc":false}]'
            instance_body['options']['skip'] = str(skip)
            instance_body['options']['take'] = str(take)
            if self.status:
                out = self.session.post(instance_url, json=instance_body)
                for item in out.json()['data']:
                    caption = item['caption']
                    ids = item['id']
                    serial = item['-1494']
                    types = item['-56855']
                    inventory = item['-1496']
                    try:
                        setup = item['-14263']['caption']
                    except TypeError:
                        setup = 'None'
                    soft_version = item['-3508']
                    comment = item['-6153']
                    try:
                        visibility = item['-13295'][0]['caption']
                    except IndexError:
                        visibility = 'None'
                    try:
                        route = item['-3134'][0]['caption']
                    except IndexError:
                        route = 'None'
                    with open('route.txt', 'a', encoding='utf8') as f:
                        f.write(
                            f'ID - {ids}\nНаименование - {caption}\n'
                            f'Серийный номер - {serial}\n'
                            f'Тип - {types}\n'
                            f'Инвентарный номер - {inventory}\n'
                            f'Место установки - {setup}\n'
                            f'Версия ПО - {soft_version}\n'
                            f'Область видимости - {visibility}\n'
                            f'Комментарий - {comment}\n'
                            f'Маршрут - {route}\n=========================\n')
                    self.route_id.append(ids)
            skip += 1000
            with open('ids.txt', 'w') as f:
                f.write(str(self.route_id))
        print(self.route_id)
        return

    @log
    def instance_meter(self, class_id):
        take = 1000  # Количество записей на странице
        skip = 0  # От какой записи
        instance_body['classId'] = class_id
        while skip < self.item_count - (self.item_count % 1000):
            instance_body['options']['sort'] = '[{"selector":"id","desc":false}]'
            instance_body['options']['skip'] = str(skip)
            instance_body['options']['take'] = str(take)
            if self.status:
                out = self.session.post(instance_url, json=instance_body)
                for item in out.json()['data']:
                    caption = item['caption']
                    ids = item['id']
                    serial = item['-1494']
                    types = item['-56855']
                    inventory = item['-1496']
                    filling = item['-32290']
                    try:
                        setup = item['-8295']['caption']
                    except TypeError:
                        setup = 'None'
                    accuracy_class = item['-3130']
                    data_issue = item['-1498']
                    data_installation = item['-32298']
                    data_last_verify = item['-2568']
                    data_next_verify = item['-22240']
                    data_withdrawal = item['-32300']
                    soft_version = item['-3508']
                    comment = item['-6153']
                    replacement = item['-32296']
                    try:
                        visibility = item['-13295'][0]['caption']
                    except IndexError:
                        visibility = 'None'
                    control_name = item['21208']
                    code = item['-1000227']
                    try:
                        route = item['-3134'][0]['caption']
                    except IndexError:
                        route = 'None'
                    info_exchange = item['28023301']
                    information = item['30396562']

                    print(f'{ids} - {types} - {serial} - {setup}')
            skip += 1000
        return

    @log
    def configurator(self, ids: list):
        for _id in ids:
            conf_url = f'{configurator_url}{_id}'
            response = self.session.get(conf_url)
            print(response.json())

    @log
    def get_reports(self):
        response = self.session.get(reports_url)
        for report in response.json():
            report_id = report.get('id')
            report_name = report.get('caption')
            group_id = report.get('groupId')
            group_name = report.get('groupCaption')
            report_comment = report.get('comment')
            offed = 'В работе' if not report.get('switchedOff') else 'Отключен'
            print(f'[{report_id}] - {report_name}. [{group_name}]. {offed}')

    @log
    def create_report(self, report_id):
        report_url = f'{create_report_url}{report_id}'
        response = self.session.get(report_url).json()
        print(response)
        print(f'Количество параметров отчета - {len(response)}')
        for param in response:
            print(param.get('parameterName'))

    @log
    def find_meter(self, serial: str, class_id):
        instance_body['classId'] = class_id
        instance_body['options']['take'] = '50'
        instance_body['options']['sort'] = '[{"selector":"id","desc":false}]'
        instance_body['options']['filter'] = f'["-1494", "contains", "{serial}"]'
        response = self.session.post(instance_url, json=instance_body).json()
        print(response)
        return response['data']

    def delete_meter(self, serial: str):
        if self.status:
            try:
                print(f'Ищем счетчик {serial}..')
                ids = self.find_meter(serial)[0]['id']
                print(f'Счетчик {serial} найден, идентификатор {ids}')
                print(f'Удаляем счетчик с идентификатором {ids}...')
                delete_body['deletingObject'].append(ids)
                params = {"mode": "cors", "method": "DELETE"}
                response = self.session.delete(delete_url, params=params, timeout=250.5, json=delete_body)
                print(response)
                print('Счетчик удален.')
            except IndexError:
                print('Счетчик не найден')

    def access_level(self):
        response = self.session.post(access_level_url, data='[-1596,-1594]').json()
        print(response)

    def __str__(self):
        return f'Token - {self.token}\nStatus - {self.status}'


if __name__ == '__main__':
    parser = PyramidParser()
    parser.count_instance(items["Каналообразующее оборудование"])
    # parser.instance_route(items["Каналообразующее оборудование"])
    parser.configurator([21521238, 21521273])
    # parser.count_branch_instance()
    # parser.instance_meter()
    # parser.get_reports()
    # parser.create_report(25614553)
    # parser.find_meter('53013169')
    # parser.access_level()
    # parser.delete_meter('009217090304629')
    # parser.find_meter('26899455')
    # parser.count_instance()
