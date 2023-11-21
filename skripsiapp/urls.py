from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.template import RequestContext
from . import views

urlpatterns = [
    path('', views.landingpage, name='landingpage'),
    path('input/', views.inputpage, name='inputpage'),
    path('menu/', views.menupage, name='menupage'),
    path('submit/', views.prosesdata, name='submit'),
    path('admin-index/', views.adminindex, name='adminindex'),
    path('admin-add-new/', views.createpage, name='createpage'),
    path('admin-save-new/', views.addmakanan, name='addnew'),
    path('admin-update-page/<id>', views.updatepage, name='updatepage'),
    path('admin-update-save/<id>', views.saveupdate, name='saveupdate'),
    path('admin-delete/<id>', views.delete, name='delete'),
    path('login-page/', views.loginpage, name='loginpage'),
    path('registrasi-page/', views.registrasipage, name='registrasipage'),
    path('user-logout/', views.user_logout, name='user-logout'),
    path('export-pdf/', views.export_pdf, name='export_pdf'),
]


