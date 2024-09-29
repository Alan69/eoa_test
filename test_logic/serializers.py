from rest_framework import serializers
from .models import Product, Test, Question, Option, Result, BookSuggestion, CompletedTest, CompletedQuestion
from accounts.models import User
from accounts.serializers import UserSerializer

# new
class CurrentOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text']

class CurrentQuestionSerializer(serializers.ModelSerializer):
    options = CurrentOptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'options']

class CurrentTestSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = ['id', 'title', 'questions']

    def get_questions(self, obj):
        questions = Question.objects.filter(test=obj)
        return CurrentQuestionSerializer(questions, many=True).data

class CurrentProductSerializer(serializers.ModelSerializer):
    tests = CurrentTestSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'tests']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'sum', 'time']

class TestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Test
        fields = ['id', 'title', 'is_required']

class CompletedOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text', 'is_correct']

class CompletedQuestionSerializer(serializers.ModelSerializer):
    options = CompletedOptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'options']

class CompletedQuestionSerializer(serializers.ModelSerializer):
    question = CurrentQuestionSerializer()
    selected_option = CurrentOptionSerializer()
    test = TestSerializer()

    class Meta:
        model = CompletedQuestion
        fields = ['id', 'test', 'question', 'selected_option']

class CompletedTestSerializer(serializers.ModelSerializer):
    completed_questions = CompletedQuestionSerializer(many=True)
    user = UserSerializer()
    product = ProductSerializer()

    class Meta:
        model = CompletedTest
        fields = ['id', 'user', 'product', 'completed_date', 'completed_time', 'completed_questions']


# old
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
