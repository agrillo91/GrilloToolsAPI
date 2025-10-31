from django.urls import path
from Maya_Plugin import views

urlpatterns = [
    path("plugin_info/", views.plugin_info, name="plugin_info"),
    path("docs/", views.docs, name="docs"),
    path("contact/", views.Contact, name="contact"),
    path("", views.index, name="index"),

]