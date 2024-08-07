from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, TestViewSet, QuestionViewSet, OptionViewSet, ResultViewSet, BookSuggestionViewSet, MultiTestQuestionView

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'tests', TestViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'options', OptionViewSet)
router.register(r'results', ResultViewSet)
router.register(r'booksuggestions', BookSuggestionViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/tests/questions/', MultiTestQuestionView.as_view(), name='multi-test-questions'),
]
