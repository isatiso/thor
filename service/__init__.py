# coding:utf-8
import sys

from config import _ENV as env
from services.manager import APP as app, QUEUE_LIST as queue_list
from services.manager import assemble_celery_cmd
from services.manager import Tasks
