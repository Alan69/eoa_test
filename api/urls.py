from accounts.views import UserDetailView, LogoutView, signup, current_user_view

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from test_logic.views import ( 
    ProductViewSet, TestViewSet, QuestionViewSet, 
    OptionViewSet, ResultViewSet, BookSuggestionViewSet, 
    product_tests_view, required_tests_by_product,
    complete_test_view
)

from dashboard.views import test_list, profile, test_history, history_detail

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'tests', TestViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'options', OptionViewSet)
router.register(r'results', ResultViewSet)
# router.register(r'booksuggestions', BookSuggestionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', signup, name='register'),
    # path('login/', login, name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('user/', UserDetailView.as_view(), name='user_detail'),
    path('user/auth/', current_user_view, name='current_user_view'),

    path('dashboard', test_list, name='test_list'),
    path('profile/', profile, name='profile'),
    path('test_history/', test_history, name='test_history'),
    path('test_history/<int:pk>/', history_detail, name='history_detail'),

    path('current/test/', product_tests_view, name='get-tests'),

    path('product/<uuid:product_id>/tests/', required_tests_by_product, name='required-tests-by-product'),

    path('complete/test/', complete_test_view, name='complete-test'),
]
