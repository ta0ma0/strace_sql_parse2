#!/usr/bin/env python3
import subprocess
import sys
import re
import warnings

def get_val(e):
  return e['Duration']

try:
    import pymysql
except ModuleNotFoundError:
    print('Устанавливаем pymysql')
    install = subprocess.Popen(['pip3', 'install', 'pymysql'], stdout=subprocess.PIPE)
    output, error = install.communicate()

select_list = []
select_list_clean = []
duration_list = []
try:
    sys.argv[1]
except IndexError:
    print('Введите аргументы: файл strace, имя базы, пароль в кавычках')
    sys.exit()

with open(sys.argv[1]) as log:
    log_list = log.readlines()
for el in log_list:

    current = re.findall(r'SELECT .+\"', el)
    if current != []:
        select_list.append(current)

for el in select_list:
    clean_select = (el[0][0:-1])
    if not re.search('\$|\@', clean_select):
        clean_select = re.sub('\\\\.', ' ', clean_select)
        select_list_clean.append(clean_select)

connection = pymysql.Connect(host='r95316mu.beget.tech',
                             user='r95316mu_parser',
                             password='br&N1Em61',
                             db='r95316mu_parser',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

with warnings.catch_warnings():
    # Ignore all warnings other than pymysql generated ones
    warnings.simplefilter("ignore")
    # warnings.simplefilter("error", category=pymysql.Warning)
    with connection.cursor() as cursor:
        sql0 = "set profiling=1"
        sql = "SELECT * FROM `wp_options` LIMIT 2"
        sql2 = "show profiles"
        cursor.execute(sql0)
        for el in select_list_clean:
            # count = 10
            # while count >= 0:
            try:
                cursor.execute(el)
                # count -= 1
            except pymysql.err.ProgrammingError as err:
                print(err)
                sys.exit()
            cursor.execute(sql2)
            duration_list.append(cursor.fetchone())

    sorted_result = sorted(duration_list, key=get_val)
    for el in sorted_result:
        print('{:<10s}{:>9f}{:^12s}{:<12s}'.format('Длительность:', el['Duration'], 'Запрос:', el['Query']))
    print('Запросов всего:', len(select_list_clean))