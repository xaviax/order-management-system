from django.urls import path
from . import views
urlpatterns = [

    # Routes for menu-item
    path('menu-items',views.MenuItemListView.as_view(), name='menu-items'),
    path('menu-items/<int:pk>',views.MenuItemDetailView.as_view(), name='menu-item-detail'),


    # Routes for manager handling
    path('groups/manager/users',views.UserGroupManager.as_view(), name="group-manager"),

    path('groups/manager/users/<int:pk>',views.ManagerDestroy.as_view(),),

    #Routes for delivery crew handling

    path('groups/delivery-crew/users',views.DeliveryCrewListCreate.as_view()),

    path('groups/delivery-crew/users/<int:pk>',views.DeliveryCrewDestroy.as_view()),

    #Routes for cart handling

    path('cart/menu-items',views.CartListCreate.as_view())





]