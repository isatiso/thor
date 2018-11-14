# coding:utf-8
"""Manager of celery tasks.
cmd: celery -A manager.app worker
        celery -A manager.app worker -l info -P gevent -c 3 -Q online_mypc_pdfconvert --hostname=online_mypc_pdfconvert@%%h
        celery -A manager.app worker -l info -P gevent -c 3 -Q online_mypc_download --hostname=online_mypc_download@%%h
        celery -A manager.app worker -l info -P gevent -c 3 -Q online_mypc_email --hostname=online_mypc_email@%%h
        celery -A manager.app worker -l info -P gevent -c 3 -Q online_mypc_database --hostname=online_mypc_database@%%h
"""
import os
import sys

from workers.manager import APP as app


if '-Q' in sys.argv:
    TASK_QUEUE = sys.argv[sys.argv.index('-Q') + 1]
    TASK_QUEUE = TASK_QUEUE.split('_')[1]
else:
    TASK_QUEUE = ''

SHOW_CONFIG = True

if TASK_QUEUE:
    __import__(f'workers.task_{TASK_QUEUE}')
else:
    SHOW_CONFIG = False

if SHOW_CONFIG:
    for i in sorted(app.conf.keys()):
        # print(i)
        if i != 'task_queues':
            print(' ' * (35 - len(i)), i, ':', app.conf.get(i))
