from huey import RedisHuey

huey = RedisHuey()

from app.util.task.tasks import example

if __name__ == '__main__':
    print('Usage:')
    print('    huey_consumer.py run_huey.huey')
    pass