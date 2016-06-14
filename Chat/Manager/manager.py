from Chat.models import *
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User


def load_group(user):
    groups = Group.objects.filter(username=user)
    return groups


def load_friend(group):
    result = []
    friends = FriendRelation.objects.filter(Q(u1_group=group) | Q(u2_group=group)).order_by('-last_chat_time')
    for i in friends:
        if i.u1_group == group:
            item = dict()
            item["username"] = i.u2_name.username
            item["num"] = i.u1_chat_num
            result.append(item)
        else:
            item = dict()
            item["username"] = i.u1_name.username
            item["num"] = i.u2_chat_num
            result.append(item)
    return result


def load_state(group):
    result = []
    friends = FriendRelation.objects.filter(Q(u1_group=group) | Q(u2_group=group)).order_by('-last_chat_time')
    for i in friends:
        if i.u1_group == group:
            result.append(i.u2_name)
        else:
            result.append(i.u1_name)
    return result


def load_user_friend(group_name, user):
    result = []
    group = Group.objects.get(group_name=group_name, username=user)
    friends = FriendRelation.objects.filter(Q(u1_group=group) | Q(u2_group=group)).order_by('-last_chat_time')
    for i in friends:
        if i.u1_group == group:
            result.append((i.u2_name.username, i.u1_chat_num, i.last_chat_time))
        else:
            result.append((i.u1_name.username, i.u2_chat_num, i.last_chat_time))
    return result


def fresh_user_friend(group_name, user):
    result = []
    group = Group.objects.get(group_name=group_name, username=user)
    friends = FriendRelation.objects.filter(Q(u1_group=group) | Q(u2_group=group)).order_by('-last_chat_time')
    for i in friends:
        if i.u1_group == group:
            state = UserInfo.objects.get(username=i.u2_name)
            result.append((i.u2_name.username, i.u1_chat_num, i.last_chat_time, state.state))
        else:
            state = UserInfo.objects.get(username=i.u1_name)
            result.append((i.u1_name.username, i.u2_chat_num, i.last_chat_time, state.state))
    return result


def load_all_friend(user):
    result = []
    group = load_group(user)
    for j in group:
        friends = load_friend(j)
        result.append(friends)
    return result


def get_username(l):
    result = []
    for i in l:
        result.append(i.username)
    return result


def get_all_username(l):
    result = []
    for i in l:
        result.append(get_username(i))
    return result


def get_groupname(l):
    result = []
    for i in l:
        result.append(i.group_name)
    return result


def ListtoJSON(self):
    res = {}
    i = 0
    for item in self:
        res[i] = ChattoJSON(item)
        i += 1
    return res


def ChattoJSON(self):
    fields = []
    for field in self._meta.fields:
        fields.append(field.name)

    d = {}
    import datetime
    for attr in fields:
        if isinstance(getattr(self, attr), datetime.datetime):
            d[attr] = getattr(self, attr).strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(getattr(self, attr), datetime.date):
            d[attr] = getattr(self, attr).strftime('%Y-%m-%d')
        elif isinstance(getattr(self, attr), models.Model):
            d[attr] = getattr(self, attr).username
        else:
            d[attr] = getattr(self, attr)
    return d
    # import json
    # return json.dumps(d)
