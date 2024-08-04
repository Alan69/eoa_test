from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Product, Test, Question, Option, Result, BookSuggestion
from .serializers import (
    ProductSerializer, TestSerializer, QuestionSerializer, 
    OptionSerializer, ResultSerializer, BookSuggestionSerializer
)
from django.shortcuts import get_object_or_404

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def purchase(self, request, pk=None):
        product = self.get_object()
        user = request.user

        if user.balance >= product.sum:
            user.balance -= product.sum
            user.save()
            return Response({'status': 'Product purchased successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    # permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def questions(self, request, pk=None):
        test = self.get_object()
        questions = Question.objects.filter(test=test)
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    # permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def options(self, request, pk=None):
        question = self.get_object()
        options = Option.objects.filter(question=question)
        serializer = OptionSerializer(options, many=True)
        return Response(serializer.data)

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
