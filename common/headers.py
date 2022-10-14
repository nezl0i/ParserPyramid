# =============================================================================================
base_url = 'http://172.18.48.206:5000/api/v1'
login_url = '/auth/login/?timeZoneOffset=-180'
instance_url = '/rdinstance/getinstances/'
count_url = '/rdinstance/getcount/'
reports_url = '/reports/getreports/'
create_report_url = '/reports/getreportparameters/?reportId='
delete_url = '/rdinstance/deleteinstances/'
access_level_url = '/rdinstance/getaccesslevel/'
configurator_url = '/xmlcfg/readxmlconfiguration/?equipmentId='

header = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "content-type": "application/json",
    "time-zone-offset": "-180",
}

login_body = {
    "newPassword": "",
    "oldPassword": "",
    "confirmPassword": "",
    "newUsername": "",
    "tokens": ""
}

instance_body = {
    # "classId": -1646,
    "userCustomized": "false",
    "options": {}
}

delete_body = {
    "deletingObject": [],
    "deleteMeterPoints": False,
    "deleteMeters": False,
    "deleteAbonents": False,
    "deleteAbonentAccounts": False
}


locate = {"Славянские ЭС": "Славянск",
          "Адыгейские ЭС": "Адыгей",
          "Армавирские ЭС": "Армавир",
          "Сочинские ЭС": "Сочинск",
          "Краснодарские ЭС": "Краснодар",
          "Тихорецкие ЭС": "Тихорецк",
          "Тимашевские ЭС": "Тимашевск",
          "Усть-Лабинские ЭС": "Усть-Лабинск",
          "Юго-Западные ЭС": "Юго-Запад",
          "Ленинградские ЭС": "Ленинград",
          "Лабинские ЭС": "Лабинск"}
