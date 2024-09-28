from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Product, Test, Question, Option, Result, BookSuggestion, CompletedTest
from .serializers import (
    ProductSerializer, TestSerializer, QuestionSerializer,
    OptionSerializer, ResultSerializer, BookSuggestionSerializer, 
    CurrentTestSerializer, CompletedTestSerializer
)
from rest_framework.decorators import api_view
from django.db.models import Sum
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.timezone import now

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        product = self.get_object()
        user = request.user

        if user.balance >= product.sum:
            user.balance -= product.sum
            user.save()
            return Response({'status': 'Product purchased successfully'}, status=status.HTTP_200_OK)
        
        return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)


class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer

    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        test = self.get_object()
        questions = Question.objects.filter(test=test).prefetch_related('option_set')
        data = QuestionSerializer(questions, many=True).data
        
        for question in data:
            question['options'] = OptionSerializer(question['options'], many=True).data
        
        return Response(data)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    @action(detail=True, methods=['get'], url_path='options')
    def get_options(self, request, pk=None):
        question = self.get_object()
        options = Option.objects.filter(question=question)
        return Response(OptionSerializer(options, many=True).data)


class OptionViewSet(viewsets.ModelViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    # permission_classes = [IsAuthenticated]


class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data
        test = get_object_or_404(Test, pk=data['test'])
        question = get_object_or_404(Question, pk=data['question'])
        selected_option = get_object_or_404(Option, pk=data['selected_option'])

        result = Result.objects.create(
            test=test,
            student=request.user,
            question=question,
            selected_option=selected_option,
            score=float(selected_option.is_correct),  # score is 1.0 for correct and 0.0 for incorrect
            is_correct=selected_option.is_correct
        )

        return Response(ResultSerializer(result).data, status=status.HTTP_201_CREATED)


class BookSuggestionViewSet(viewsets.ModelViewSet):
    queryset = BookSuggestion.objects.all()
    serializer_class = BookSuggestionSerializer
    permission_classes = [IsAuthenticated]


@swagger_auto_schema(
    method='post',
    operation_description="Retrieve tests and their questions based on product and test IDs",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['product_id', 'tests_ids'],
        properties={
            'product_id': openapi.Schema(type=openapi.TYPE_STRING, description='UUID of the product'),
            'tests_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), description='List of test UUIDs')
        }
    ),
    responses={
        200: openapi.Response(
            description="Test data with questions and options",
            examples={
                "application/json": {
                    "time": 90,
                    "tests": [
                        {
                            "id": "some-test-uuid-1",
                            "title": "Test 1",
                            "questions": [
                                {
                                    "id": "some-question-uuid-1",
                                    "text": "What is the capital of France?",
                                    "options": [
                                        {
                                            "id": "some-option-uuid-1",
                                            "text": "Paris"
                                        },
                                        {
                                            "id": "some-option-uuid-2",
                                            "text": "London"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        ),
        404: openapi.Response(description="Product not found"),
    }
)
@api_view(['POST'])
def product_tests_view(request):
    product_id = request.data.get('product_id')
    tests_ids = request.data.get('tests_ids')

    # Validate request data
    if not product_id or not isinstance(tests_ids, list):
        return Response({"detail": "Invalid input data"}, status=status.HTTP_400_BAD_REQUEST)

    # Get the product
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    # Get the tests based on the provided IDs
    tests = Test.objects.filter(product=product, id__in=tests_ids)

    # Get total time for all tests
    total_time = tests.aggregate(total_time=Sum('time'))['total_time'] or 0

    # Serialize the tests
    serialized_tests = CurrentTestSerializer(tests, many=True).data

    # Return the response
    return Response({
        "time": total_time,
        "tests": serialized_tests
    }, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="Retrieve required tests for a given product ID",
    responses={
        200: openapi.Response(
            description="List of required tests",
            examples={
                "application/json": [
                    {
                        "id": "some-test-uuid-1",
                        "title": "Required Test 1",
                        "is_required": True
                    },
                    {
                        "id": "some-test-uuid-2",
                        "title": "Required Test 2",
                        "is_required": True
                    }
                ]
            }
        ),
        404: openapi.Response(description="Product not found"),
    }
)
@api_view(['GET'])
def required_tests_by_product(request, product_id):
    # Get the product
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    # Filter tests by product and where is_required is True
    required_tests = Test.objects.filter(product=product)

    # Serialize the tests
    serialized_tests = TestSerializer(required_tests, many=True).data

    # Return the response
    return Response(serialized_tests, status=status.HTTP_200_OK)




@swagger_auto_schema(
    method='post',
    operation_description="Submit a completed test and get completion data",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['product_id', 'tests_ids', 'product_score', 'tests_score'],
        properties={
            'product_id': openapi.Schema(type=openapi.TYPE_STRING, description='UUID of the product'),
            'tests_ids': openapi.Schema(
                type=openapi.TYPE_ARRAY, 
                items=openapi.Items(type=openapi.TYPE_STRING), 
                description='List of test UUIDs'
            ),
        }
    ),
    responses={
        201: openapi.Response(
            description="Completed test data with product and test scores, including questions and options",
            examples={
                "application/json": {
                    "id": "some-completed-test-uuid",
                    "completed_date": "2024-01-01",
                    "completed_time": "15:30:00",
                    "user": {
                        "id": 1,
                        "username": "student1",
                        "email": "student1@example.com"
                    },
                    "product": {
                        "id": "some-product-uuid",
                        "title": "Product 1"
                    },
                    "product_score": 85.0,
                    "tests_score": 90.0,
                    "tests": [
                        {
                            "id": "some-test-uuid-1",
                            "title": "Test 1",
                            "questions": [
                                {
                                    "id": "some-question-uuid-1",
                                    "text": "What is the capital of France?",
                                    "options": [
                                        {
                                            "id": "some-option-uuid-1",
                                            "text": "Paris",
                                            "is_correct": "true"
                                        },
                                        {
                                            "id": "some-option-uuid-2",
                                            "text": "London",
                                            "is_correct": "false"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        ),
        400: openapi.Response(description="Invalid input data"),
        404: openapi.Response(description="Product not found"),
    }
)
@api_view(['POST'])
def complete_test_view(request):
    user = request.user
    product_id = request.data.get('product_id')
    tests_ids = request.data.get('tests_ids')

    # Validate request data
    if not product_id or not isinstance(tests_ids, list):
        return Response({"detail": "Invalid input data"}, status=status.HTTP_400_BAD_REQUEST)

    # Get the product
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    # Get the tests
    tests = Test.objects.filter(id__in=tests_ids)

    # Ensure that questions and options are loaded for each test
    for test in tests:
        test.questions = Question.objects.filter(test=test).prefetch_related('options')

    # Create the CompletedTest instance
    completed_test = CompletedTest.objects.create(
        user=user,
        product=product,
        completed_date=now().date(),
        completed_time=now().time()
    )

    # Add tests to the CompletedTest instance
    completed_test.tests.set(tests)
    completed_test.save()

    # Serialize the completed test
    serialized_completed_test = CompletedTestSerializer(completed_test).data

    # Return the response
    return Response(serialized_completed_test, status=status.HTTP_201_CREATED)