#!/usr/bin/env python
# coding=utf-8
from django.contrib.auth.models import User
from django import forms


class RegisterForm(forms.Form):
    username = forms.CharField(
        label='UserName',
        help_text='Username can be used to login, without blank or @。',
        max_length=20,
        initial='',
        widget=forms.TextInput(attrs={'class': 'user'}),
        )

    email = forms.EmailField(
        label='MailBox',
        help_text='MailBox can be used to login, and you can retrieve your password by it',
        max_length=50,
        initial='',
        widget=forms.TextInput(attrs={'class': 'mail'}),
        )

    password = forms.CharField(
        label='Password',
        help_text=u'The length should be between 6 ~ 18 。',
        min_length=6,
        max_length=18,
        widget=forms.PasswordInput(attrs={'class': 'pass'}),
        )

    confirm_password = forms.CharField(
        label='Password again',
        min_length=6,
        max_length=18,
        widget=forms.PasswordInput(attrs={'class': 'pass'}),
        )

    def clean_username(self):
        username = self.cleaned_data['username']
        if ' ' in username or '@' in username:
            raise forms.ValidationError('Can\'t not include blank or @!')
        res = User.objects.filter(username=username)
        if len(res) != 0:
            raise forms.ValidationError('This user name is already used!')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        res = User.objects.filter(email=email)
        if len(res) != 0:
            raise forms.ValidationError('This Mailbox is already used')
        return email

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError('The password are not the same you type, please try again')

    def save(self):
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        user = User.objects.create_user(username, email, password)
        user.save()