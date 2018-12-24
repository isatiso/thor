# coding:utf-8
import sys

from config import _ENV as env
from tasks.manager import APP as app, QUEUE_LIST as queue_list
from tasks.manager import assemble_celery_cmd
from tasks.manager import Tasks
