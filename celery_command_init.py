import os
from workers import queue_list, assemble_celery_cmd
from config.config import _ENV as env


if __name__ == '__main__':

    print('dev')
    celery_startup_file = f'celery_{env}_up.bat'
    if os.path.exists(celery_startup_file):
        os.remove(celery_startup_file)

    for queue in queue_list:
        celery_local_file = f'scripts\\{env}_{queue}.bat'
        celery_command = f'title {queue}\n cd /D %~dp0.. && '
        celery_command += ' '.join(assemble_celery_cmd(queue))

        open(celery_local_file, 'wb+').write(str.encode(celery_command))

        open(celery_startup_file,
             'ab+').write(str.encode(f'start {celery_local_file}\n'))

    print('done')
