# coding:utf-8
"""Module of celery task queue manager."""
import os
import traceback

from celery import Celery

from lib.arguments import Arguments
from config import CFG as O_O, _ENV as env

CELERY_CMD = os.getenv('celery_cmd', default='celery')

QUEUE_LIST = {
    'message': (5, 'gevent', 'info'),
    'db': (100, 'gevent', 'info'),
    'oss': (5, 'gevent', 'info'),
}

APP = Celery(
    'tasks',
    backend=O_O.celery.backend,
    broker=O_O.celery.broker,
)

APP.conf.update(
    task_serializer='json',
    result_serializer='json',
    result_expires=1800,
    task_default_queue='default',
    task_default_exchange='tasks',
    task_default_exchange_type='topic',
    task_default_routing_key='task.default',
    task_routes={
        f'workers.task_{q}.*': {
            'queue': f'{env}_{q}'
        }
        for q in QUEUE_LIST
    })


def assemble_celery_cmd(queue):
    concurrency, parallel, loglevel = QUEUE_LIST[queue]
    return (f'{CELERY_CMD}', 'worker', '-A', 'worker.app', '-c',
            f'{concurrency}', '-P', f'{parallel}', '-Q', f'{env}_{queue}',
            '-n', f'{env}_{queue}@%h', f'--loglevel={loglevel}')


class Tasks(Arguments):
    """Tasks Wrapper."""

    def __getattr__(self, name):
        return self[name]
