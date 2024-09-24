from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Product, Test, Question, Option, Result, BookSuggestion
from .serializers import (
    ProductSerializer, TestSerializer, QuestionSerializer,
    OptionSerializer, ResultSerializer, BookSuggestionSerializer
)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    
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
    permission_classes = [IsAuthenticated]


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
