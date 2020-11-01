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
    import pymysql

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

connection = pymysql.Connect(host='localhost',
                             user=sys.argv[2],
                             password=sys.argv[3],
                             db=sys.argv[2],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

with warnings.catch_warnings():
    # Ignore all warnings other than pymysql generated ones
    warnings.simplefilter("ignore")
    # warnings.simplefilter("error", category=pymysql.Warning)
    with connection.cursor() as cursor:
        sql0 = "set profiling=1"
        sql2 = "show profiles"
        cursor.execute(sql0)
        for el in select_list_clean:
            try:
                cursor.execute(el)
            except pymysql.err.ProgrammingError as err:
                print(err)
                print(el)
                continue
            cursor.execute(sql2)
            duration_list.append(cursor.fetchone())

    sorted_result = sorted(duration_list, key=get_val)
    all_time_query = 0
    for el in sorted_result:
        print('{:<10s}{:>9f}{:^12s}{:<12s}'.format('Длительность:', el['Duration'], 'Запрос:', el['Query']))
        all_time_query += el['Duration']
    print('Запросов всего:', len(select_list_clean), 'Общая длительность:', round(all_time_query, 4), 'сек')
