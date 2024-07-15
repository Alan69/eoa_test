from django.urls import path
from .views import test_detail, take_test, test_result, product_detail

urlpatterns = [
    path('products/<int:pk>/', product_detail, name='product_detail'),
    
    path('test-detail/', test_detail, name='test_detail'),
    path('take/<int:pk>/', take_test, name='take_test'),
    path('take/<int:pk>/<int:question_index>/', take_test, name='take_test'),
    path('result/<int:pk>/', test_result, name='test_result'),
]