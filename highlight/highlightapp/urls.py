from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("edit/<str:language>/", views.highlightc, name="highlight"),
    path("pdf/<str:language>/", views.topdf, name="pdf")
]