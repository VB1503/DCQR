
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import HomePageView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('admin/', admin.site.urls,name='admin'),
    path('accounts/', include("accounts.urls")),
    

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)