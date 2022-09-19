from time import sleep

import requests

url = 'https://egrul.nalog.ru'
url_1 = 'https://egrul.nalog.ru/search-result/'
url_2 = 'https://egrul.nalog.ru/vyp-download/'
inn = 2540167061

s = requests.Session()
s.get(url + '/index.html')
# print(s.cookies)

r = s.post(url, data={'query': inn}, cookies=s.cookies)
# print(r.json()['t'])

r1 = s.get(url_1 + r.json()['t'], cookies=s.cookies)
print(r1.json()['rows'][0]['a'])
print(r1.json()['rows'][0]['g'])
print(f"ИНН: {r1.json()['rows'][0]['i']}")
print(f"ОГРН: {r1.json()['rows'][0]['o']}")
print(f"Дата присвоения ОГРН: {r1.json()['rows'][0]['r']}")
print(f"КПП: {r1.json()['rows'][0]['p']}")
# print(r1.json()['rows'][0]['t'])

r2 = s.get(url_2 + r1.json()['rows'][0]['t'], cookies=s.cookies)
print(r2.content)
sleep(2)
with open(f'{r1.json()["rows"][0]["n"]}_{str(inn)}.pdf', 'wb') as f:
    f.write(r2.content)
