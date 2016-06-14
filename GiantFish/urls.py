"""GiantFish URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from Chat import views as chat_views
from views import RegisterView, logout_view
# from users import urls as users_urls
from django.conf.urls import include

urlpatterns = [
    url(r'^logout/', logout_view),
    url(r'^$', chat_views.index, name='chat'),
    url(r'^admin/', admin.site.urls),
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^post/$', chat_views.post),
    # url(r'^accounts/', include('users.urls')),
]
