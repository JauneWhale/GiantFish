from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from forms import RegisterForm
from Chat.models import Group, UserInfo
import logging


# logout the user
def logout_view(request):
    tu = UserInfo.objects.get(username=request.user)
    tu.state = 'F'
    tu.save()
    logout(request)
    return HttpResponseRedirect(reverse('login'))


class RegisterView(FormView):
    template_name = 'register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('chat')

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        # logging.debug(username)
        user_obj = User.objects.get(username=username)
        Group.objects.create(group_name="Friend", username=user_obj)
        UserInfo.objects.create(username=user_obj, state="T", gender="N")
        return super(RegisterView, self).form_valid(form)
