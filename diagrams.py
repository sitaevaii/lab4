#from jira import JIRA
import requests
import json
import numpy as np
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from collections import defaultdict
import pandas as pd
from collections import Counter
import datetime

URL = 'https://issues.apache.org/jira/rest/api/2/search'

payload = {
        'jql': '',
        'maxResults': '1000',
        'expand': 'changelog',
        'fields': 'created,resolutiondate'
    }
def get_issues(URL, payload):
    response = requests.get(URL, params=payload)
    if response.status_code != 200:
        print(f"Ошибка {response.status_code}")
        return []
    else:
        return json.loads(response.text)

def hist1():
    payload['jql']='project=HDFS AND status=Closed ORDER BY createdDate'
    data = get_issues(URL, payload)
    open = []
    for issue in data['issues']:
        creating_date = issue['fields']['created']
        resolution_date = issue['fields']['resolutiondate']

        created = datetime.datetime.strptime(creating_date, '%Y-%m-%dT%H:%M:%S.%f%z')
        resolved = datetime.datetime.strptime(resolution_date, '%Y-%m-%dT%H:%M:%S.%f%z')
        open.append((resolved - created).total_seconds() / (60 * 60 * 24))

    plt.figure(figsize=(10, 6))
    plt.hist(open, bins=20, edgecolor='black', color='green')
    plt.title('Длительность периода задач в открытом состоянии')
    plt.xlabel('Время в открытом состоянии (дни)')
    plt.ylabel('Количество задач')
    plt.show()
# hist1()
def diag2():
    payload['jql'] = 'project=HDFS AND status=Closed ORDER BY createdDate'
    data = get_issues(URL, payload)
    state_time = {}
    for issue in data['issues']:
        creating_date = issue['fields']['created']
        resolution_date = issue['fields']['resolutiondate']
        created = datetime.datetime.strptime(creating_date, '%Y-%m-%dT%H:%M:%S.%f%z')
        resolved = datetime.datetime.strptime(resolution_date, '%Y-%m-%dT%H:%M:%S.%f%z')

        changelog = issue['changelog']['histories']
        status_time = created
        status = None

        for change in changelog:
            for item in change['items']:
                if item['field'] == 'status':
                    to_status = item['toString']
                    change_time = datetime.datetime.strptime(change['created'], '%Y-%m-%dT%H:%M:%S.%f%z')
                    if to_status not in state_time:
                        state_time[to_status] = []

                    if status is not None:
                        state_time[status].append(
                            (change_time - status_time).total_seconds() / (60 * 60 * 24))  # в днях
                    status_time = change_time
                    status = to_status

        if 'Closed' not in state_time:
            state_time['Closed'] = []

        time_in_state = abs((resolved - status_time).total_seconds() / (60 * 60 * 24))  # в днях
        state_time['Closed'].append(time_in_state)

    num = 0
    plt.figure(figsize=(16, 16))
    for state, time in state_time.items():
        num+=1
        plt.subplot(2,3,num)
        plt.subplots_adjust(wspace=0.2, hspace=0.4)
        plt.hist(time, bins = 20, edgecolor='black', color='green')
        plt.title(f'Статус = {state}')
        plt.xlabel('Длительность статуса')
        plt.ylabel('Количество задач')
    plt.show()

def graf3():
    today = datetime.date.today()
    month_ago = today - timedelta(days=90)
    today, month_ago= today.strftime('%Y-%m-%d'), month_ago.strftime('%Y-%m-%d')
    payload['jql'] = f'project= HDFS AND  created>= {month_ago} AND created <= {today} ORDER BY createdDate'

    task_dates = defaultdict(lambda:{'opened': 0, 'closed': 0})
    data = get_issues(URL, payload)
    for issue in data['issues']:
        creating_date = issue['fields']['created'][5:-18]
        task_dates[creating_date]['opened']+=1
        if issue['fields'].get('resolutiondate') != None:
            resolution_date = issue['fields'].get('resolutiondate')[5:-18]
            task_dates[resolution_date]['closed']+=1

    dates = sorted(task_dates.keys())
    opened = [task_dates[date]['opened']for date in dates]
    closed = [task_dates[date]['closed'] for date in dates]

    opened_cum = pd.Series(opened).cumsum()
    closed_cum = pd.Series(closed).cumsum()


    plt.figure(figsize=(12, 8))
    plt.subplot(2,1,1)
    plt.plot(dates, opened, label = ' opened',  color = 'red', marker = 'o')
    plt.plot(dates, closed,label = 'closed', color = 'green', marker = 'o')
    plt.legend()
    plt.xlabel("Дни")
    plt.ylabel("Открытые и закрыте задачи")
    plt.xticks(dates, rotation=45)
    plt.yticks(range(5))

    plt.subplot(2, 1, 2)
    plt.plot(dates, opened_cum, label='cumulative open', color='red', marker = 'o')
    plt.plot(dates, closed_cum,label = 'cumulative closed',  color='green', marker = 'o')
    plt.legend()
    plt.xlabel("Дни")
    plt.ylabel("Открытые и закрыте задачи")
    plt.xticks(dates, rotation=45)

    plt.show()

def find_greate_user():
    payload['jql'], payload['fields'] = 'project = HDFS ORDER BY createdDate', 'assignee,reporter'
    data = get_issues(URL, payload)

    user_tasks = defaultdict(int)
    for issue in data['issues']:
        if issue['fields'].get('assignee', None):
            user_tasks[issue['fields']['assignee'].get('displayName', 'Unknown')] += 1
        if issue['fields'].get('reporter', None):
            user_tasks[issue['fields']['reporter'].get('displayName', 'Unknown')] += 1

    top_30 = sorted(user_tasks.items(), key=lambda x: x[1], reverse=True)[:30]
    return top_30
def graf4():
    top_30 = find_greate_user()
    names = [names for names, count in top_30]
    count = [count for names, count in top_30]
    plt.figure(figsize=(10, 6))
    plt.barh(names,count,  color='green')
    plt.xlabel('Количество задач')
    plt.ylabel('Имя пользователя')
    plt.title('Топ-30 активных пользователей')
    plt.show()

def graf6():
    priorities = ['Trivial', 'Minor', 'Major', 'Critical', 'Blocker']
    count_prio = []
    for priority in priorities:
        payload1 = {'jql': f'project=HDFS AND priority = {priority}', 'maxResults': '100', 'fields': 'priority'}
        data = get_issues(URL, payload1)
        count_prio.append(int(data['total']))

    plt.figure(figsize=(8, 16))
    plt.plot(count_prio, color='green', marker='o')
    plt.title(f'График количество задач по степени серьезности')
    plt.xlabel('Приоритет')
    plt.ylabel('Количество задач')
    plt.yticks(count_prio, fontsize=6, rotation=45)
    x_list = [0, 1, 2, 3, 4]
    plt.xticks(x_list, labels=priorities)
    plt.show()
