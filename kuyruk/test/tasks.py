from time import sleep

from kuyruk import Kuyruk, Task
from kuyruk.events import task_prerun, task_postrun, task_success


kuyruk = Kuyruk()
# These functions below needs to be at module level in order that
# Kuyruk worker to determine their fully qualified name.


@kuyruk.task
def print_task(message):
    print message


@kuyruk.task(queue='another_queue')
def print_task2(message):
    print message


@kuyruk.task
def raise_exception():
    return 1 / 0


@kuyruk.task(retry=1)
def retry_task():
    return 1 / 0


@kuyruk.task
def loop_forever():
    while 1:
        print 'looping forever'
        sleep(1)


@kuyruk.task(eager=True)
def eager_task():
    eager_called.append(1)
eager_called = []


@kuyruk.task
def rejecting_task():
    raise kuyruk.Reject


@kuyruk.task
def sleeping_task(seconds):
    sleep(seconds)


# Another kuyruk instance for testing before and after task decorators
kuyruk2 = Kuyruk()


@kuyruk2.task
def task_with_functions(message):
    print message
    return 42


@kuyruk2.on_prerun
def function1(sender, task, args, kwargs):
    print 'function1'
    print sender, task, args, kwargs
    assert sender is kuyruk2
    assert isinstance(task, Task)
    assert args == ['hello world']
    assert kwargs == {}


@task_with_functions.on_prerun
def function2(sender, task, args, kwargs):
    print 'function2'


@task_with_functions.on_success
def function3(sender, task, args, kwargs, return_value):
    print 'function3'
    assert return_value == 42


@task_with_functions.on_postrun
def function4(sender, task, args, kwargs):
    print 'function4'


@kuyruk2.on_postrun
def function5(sender, task, args, kwargs):
    print 'function5'


class Cat(object):

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return "Cat(%r, %r)" % (self.id, self.name)

    @classmethod
    def get(cls, id):
        if id == 1:
            return cls(1, 'Felix')

    @kuyruk.task
    def meow(self, message):
        print "Felix says:", message


class DatabaseTask(Task):

    _session = None

    def setup(self):
        self.connect_signal(task_postrun, self.close_session)

    @property
    def session(self):
        if self._session is None:
            print 'Opening session'
            self._session = object()
        return self._session

    def close_session(self, sender, task, args, kwargs):
        if self._session:
            print 'Closing session'
            self._session = None


@kuyruk.task(task_class=DatabaseTask)
def use_session():
    print use_session.session
