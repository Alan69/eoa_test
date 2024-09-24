from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import RegisterView, CustomTokenObtainPairView, UserDetailView, LogoutView, signup, login, current_user_view

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from test_logic.views import ProductViewSet, TestViewSet, QuestionViewSet, OptionViewSet, ResultViewSet, BookSuggestionViewSet

from dashboard.views import test_list, profile, test_history, history_detail

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'tests', TestViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'options', OptionViewSet)
router.register(r'results', ResultViewSet)
router.register(r'booksuggestions', BookSuggestionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', signup, name='register'),
    path('login/', login, name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/', UserDetailView.as_view(), name='user_detail'),
    path('user/auth/', current_user_view, name='current_user_view'),

    path('dashboard', test_list, name='test_list'),
    path('profile/', profile, name='profile'),
    path('test_history/', test_history, name='test_history'),
    path('test_history/<int:pk>/', history_detail, name='history_detail'),
]
