from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Product, Test, Question, Option, Result, BookSuggestion
from .serializers import (
    ProductSerializer, TestSerializer, QuestionSerializer, 
    OptionSerializer, ResultSerializer, BookSuggestionSerializer
)
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.decorators import api_view

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        product = self.get_object()
        user = request.user

        # if user.balance >= product.sum:
        #     user.balance -= product.sum
        #     user.save()
        return Response({'status': 'Product purchased successfully'}, status=status.HTTP_200_OK)
        # else:
            # return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer

    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        test = self.get_object()
        questions = Question.objects.filter(test=test)
        data = []
        for question in questions:
            options = Option.objects.filter(question=question)
            question_data = QuestionSerializer(question).data
            question_data['options'] = OptionSerializer(options, many=True).data
            data.append(question_data)
        return Response(data)

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    @action(detail=True, methods=['get'])
    def options(self, request, pk=None):
        question = self.get_object()
        options = Option.objects.filter(question=question)
        serializer = OptionSerializer(options, many=True)
        data = {
            "id": question.id,
            "text": question.text,
            "options": serializer.data
        }
        return Response(data)

    @action(detail=False, methods=['get'])
    def next_question(self, request):
        # Implement logic to fetch the next question based on the test ID and previous answers.
        # This is a placeholder example.
        test_id = request.query_params.get('test_id')
        # Fetch the next question logic here
        question = Question.objects.filter(test__id=test_id).first()
        if question:
            serializer = QuestionSerializer(question)
            return Response(serializer.data)
        return Response({"error": "No more questions"}, status=404)

class MultiTestQuestionView(APIView):
    def get(self, request, *args, **kwargs):
        test_ids = request.GET.getlist('test_id')
        if not test_ids:
            return Response({"detail": "No test IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

        questions = Question.objects.filter(test_id__in=test_ids).distinct()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_test_questions(request):
    test_ids = request.GET.getlist('test_id[]')
    if not test_ids:
        return JsonResponse({'error': 'No test IDs provided'}, status=400)

    questions = Question.objects.filter(test__id__in=test_ids).order_by('?')
    questions_data = [
        {
            'id': question.id,
            'text': question.text,
            'options': [{'id': option.id, 'text': option.text} for option in question.option_set.all()]
        }
        for question in questions
    ]
    return JsonResponse(questions_data, safe=False)

class OptionViewSet(viewsets.ModelViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    # permission_classes = [IsAuthenticated]

class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    # permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data
        test = get_object_or_404(Test, pk=data['test'])
        question = get_object_or_404(Question, pk=data['question'])
        selected_option = get_object_or_404(Option, pk=data['selected_option'])
        is_correct = selected_option.is_correct
        score = 1.0 if is_correct else 0.0

        result = Result.objects.create(
            test=test,
            student=request.user,
            question=question,
            selected_option=selected_option,
            score=score,
            is_correct=is_correct
        )

        return Response(ResultSerializer(result).data, status=status.HTTP_201_CREATED)

class BookSuggestionViewSet(viewsets.ModelViewSet):
    queryset = BookSuggestion.objects.all()
    serializer_class = BookSuggestionSerializer
    permission_classes = [IsAuthenticated]
