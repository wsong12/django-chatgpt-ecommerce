from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
	
	path("", views.HomeView.as_view(), name="home"),
	path("name_generator/", views.NameGenerator.as_view(), name="name_generator"),
    path("generate-logo/", views.GenerateLogoView.as_view(), name="generate-logo"),
]