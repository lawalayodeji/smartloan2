
from django.urls import include, path
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from loanApp import views


urlpatterns = [
    path('', views.home, name='home'),    
    path("", include('blockchain.urls')),
    path("user/", include('siteuser.urls')),
    path("admin/", admin.site.urls),
    path('bankManger/', include('bankAdmin.urls')),
    path('account/', include('loginApp.urls')),
    path('loan/', include('loanApp.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = 'loanApp.views.error_404_view'
