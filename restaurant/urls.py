from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.index, name='index'),
    path('menu/<int:table_id>/', views.menu, name='menu'),
    path('order/add/', views.add_to_order, name='add_to_order'), # API to add/update item in session/db temp
    path('order/submit/<int:table_id>/', views.submit_order, name='submit_order'),
    path('order/status/<int:table_id>/', views.order_status, name='order_status'),
    path('order/bill/<int:table_id>/', views.bill, name='bill'),
    path('order/pdf/<int:order_id>/', views.download_pdf, name='download_pdf'),
    path('order/clear/<int:table_id>/', views.clear_session, name='clear_session'),
    
    # Kitchen
    path('kitchen/', views.kitchen_dashboard, name='kitchen_dashboard'),
    path('kitchen/update/', views.update_order_status, name='update_order_status'),

    # Manager
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/menu/', views.menu_manage, name='menu_manage'),
    path('manager/menu/add/', views.menu_add, name='menu_add'),
    path('manager/menu/edit/<int:item_id>/', views.menu_edit, name='menu_edit'),
    path('manager/menu/delete/<int:item_id>/', views.menu_delete, name='menu_delete'),
    path('manager/table/clear/<int:table_id>/', views.force_clear_table, name='force_clear_table'),
]
