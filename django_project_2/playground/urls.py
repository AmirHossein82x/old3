from django.urls import path
from django.urls import include
from . import views
import debug_toolbar

urlpatterns = [
    path('hello/', views.say_hello, name='hello'),
    path('__debug__/', include(debug_toolbar.urls))
    ]