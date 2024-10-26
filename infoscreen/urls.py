from django.urls import path

from . import views

urlpatterns = [
    path('', views.index_view, name='infoscreen_index'),
    path('new-content/', views.new_content_form,
         name='infoscreen_new_content'),
    path('schedule/', views.schedule_view,
         name='infoscreen_view_schedule'),
    path('schedule/generate', views.schedule_generate,
         name='infoscreen_generate_schedule'),
]
