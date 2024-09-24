from rest_framework import serializers
from .models import Product, Test, Question, Option, Result, BookSuggestion
from accounts.models import User

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class TestSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Test
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product'] = ProductSerializer(instance.product).data
        representation['created_by'] = instance.created_by.id
        return representation


class QuestionSerializer(serializers.ModelSerializer):
    test = serializers.PrimaryKeyRelatedField(queryset=Test.objects.all())

    class Meta:
        model = Question
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['test'] = instance.test.id
        return representation


class OptionSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())

    class Meta:
        model = Option
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['question'] = instance.question.id
        return representation


class ResultSerializer(serializers.ModelSerializer):
    test = serializers.PrimaryKeyRelatedField(queryset=Test.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    selected_option = serializers.PrimaryKeyRelatedField(queryset=Option.objects.all())

    class Meta:
        model = Result
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['test'] = instance.test.id
        representation['student'] = instance.student.id
        representation['question'] = instance.question.id
        representation['selected_option'] = instance.selected_option.id
        return representation


class BookSuggestionSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())

    class Meta:
        model = BookSuggestion
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['question'] = instance.question.id
        return representation
