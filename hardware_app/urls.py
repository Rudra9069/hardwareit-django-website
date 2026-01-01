from django.urls import path, include
from . import views

urlpatterns = [
    # Main
    path('signup_page',views.signup_page, name='signup_page'),
    path('login_page',views.login_page, name='login_page'),
    path('home_page',views.home_page, name='home_page'),
    path('products_page',views.products_page, name='products_page'),
    path('about_page',views.about_page, name='about_page'),
    path("contact_page", views.contact_page, name="contact_page"),
    path("cart_page/", views.cart_page, name="cart_page"),
    path("add_to_cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("remove-from-cart/<int:cart_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("delete-from-cart/<int:cart_id>/", views.delete_from_cart, name="delete_from_cart"),
    path("checkout_page/", views.checkout_page, name="checkout_page"),
    path("place_order/", views.place_order, name="place_order"),
    path("order_success/<int:order_id>/", views.order_success, name="order_success"),
    path('logout',views.logout, name='logout'),
]