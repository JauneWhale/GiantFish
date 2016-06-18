from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
import ast


class Group(models.Model):
    group_name = models.CharField(max_length=30)
    username = models.ForeignKey(User)

    def __unicode__(self):
        return self.group_name

    class Meta:
        unique_together = ("group_name", "username")


class FriendRelation(models.Model):
    u1_name = models.ForeignKey(User, related_name='u1_name')
    u2_name = models.ForeignKey(User, related_name='u2_name')
    u1_group = models.ForeignKey(Group, related_name='u1_group')
    u2_group = models.ForeignKey(Group, related_name='u2_group')
    u1_nickname = models.CharField(max_length=30, null=True)
    u2_nickname = models.CharField(max_length=30, null=True)
    u1_chat_num = models.IntegerField(default=0)
    u2_chat_num = models.IntegerField(default=0)
    last_chat_time = models.DateTimeField(auto_now=True, null=True)

    def __unicode__(self):
        return self.u1_name.username+','+self.u2_name.username

    class Meta:
        unique_together = ("u1_name", "u2_name")


class Chat(models.Model):
    sender = models.ForeignKey(User, related_name='has_chats')
    receiver = models.ForeignKey(User)
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True, null=True)


class UserInfo(models.Model):
    GENDER_CHOICES = (
        (u'M', u'Male'),
        (u'F', u'Female'),
        (u"N", u'Unknown')
    )
    STATUS_CHOICES = (
        (u'T', u'Online'),
        (u'F', u'Offline'),
    )
    username = models.ForeignKey(User, primary_key=True)
    state = models.CharField(max_length=2, choices=STATUS_CHOICES)
    signature = models.TextField(max_length=140, null=True)
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES)
