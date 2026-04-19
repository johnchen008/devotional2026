from django.urls import path
from .views import home, daily_page

app_name = "pages"

urlpatterns = [
    path("", home, name="home"),
    path("<slug:page_date>/", daily_page, name="daily_page"),
]
