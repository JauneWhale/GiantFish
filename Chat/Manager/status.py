from Chat.models import *
from time import sleep
import threading
import Queue


# Const Stat for user control
def enum(**enums):
    return type('Enum', (), enums)

# message type enum
MSG = enum(
    FRIEND_REQUEST=2,
    FRIEND_DELETE=3,
    FRIEND_ACCEPT=4,
)


# Store the Information for the Friend Message, including sender, receiver, content and msg_type
class UserMessage:
    def __init__(self, sender, receiver, content, msg_type):
        self.sender = sender
        self.receive = receiver
        self.content = content
        self.msg_type = msg_type


# The state of one user that store its:
#       friend command queue
#       online or offline
#       active rest time ( to automatically kick the user outline )
#       if new chat come
class StatOfUser:
    user_rest_time = 60/5

    def __init__(self, user):
        self.msg = Queue.Queue(maxsize=10)
        self.stat = True
        self.rest = self.user_rest_time
        self.user = user
        self.new_chat = False
        tu = UserInfo.objects.get(username=user)
        tu.state = 'T'
        tu.save()

    def user_online(self):
        self.stat = True
        self.rest = self.user_rest_time
        tu = UserInfo.objects.get(username=self.user)
        tu.state = 'T'
        tu.save()

    def reduce_rest_time(self):
        if not self.stat:
            return False
        elif self.rest == 0:
            self.stat = False
            tu = UserInfo.objects.get(username=self.user)
            tu.state = 'F'
            tu.save()
            return True
        else:
            self.rest -= 1
            return False


class Status(threading.Thread):
    active_user = {}

    def __init__(self):
        threading.Thread.__init__(self)

    def add_active_user(self, user):
        name = user.username
        if name not in self.active_user.keys():
            self.active_user[name] = StatOfUser(user)
        else:
            self.active_user[name].user_online()

    def reduce_rest_time(self):
        for i in self.active_user:
            self.active_user[i].reduce_rest_time()

    def get_user_msg(self, name):
        user_msg_queue = self.active_user[name].msg
        if not user_msg_queue.empty():
            return user_msg_queue.get()
        return False

    def add_unread_flag(self, user):
        name = user.username
        if name not in self.active_user.keys():
            self.active_user[name] = StatOfUser(user)
            self.active_user[name].state = 'F'
        self.active_user[name].new_chat = True

    def remove_unread_flag(self, user):
        name = user.username
        if name not in self.active_user.keys():
            self.active_user[name] = StatOfUser(user)
            self.active_user[name].state = 'F'
        self.active_user[name].new_chat = False

    def run(self):
        while True:
            self.reduce_rest_time()
            # print self.active_user
            sleep(5)

