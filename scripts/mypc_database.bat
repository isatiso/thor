title database
 cd /D %~dp0.. && celery worker -A worker.app -c 20 -P gevent -Q mypc_database -n mypc_database@%h --loglevel=info