
from workers import Tasks
from workers.task_database.user import TASK_DICT as USER_TASK


TASK_DICT = sum([
    USER_TASK,
], [])

# TASKS = Tasks(DATABASE_TASK)

print(dict([(task.__name__, task) for task in TASK_DICT]))
DATABASE_TASK = Tasks(dict([(task.__name__, task) for task in TASK_DICT]))
