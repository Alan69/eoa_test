from rest_framework import serializers
from .models import Product, Test, Question, Option, Result, BookSuggestion, CompletedTest
from accounts.models import User

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
        fields = '__all__'

class TestSerializer(serializers.ModelSerializer):
    # product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = Test
        fields = ['id', 'title', 'is_required']

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation['product'] = ProductSerializer(instance.product).data
    #     return representation




class CompletedOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text', 'is_correct']

class CompletedQuestionSerializer(serializers.ModelSerializer):
    options = CompletedOptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'options']

class CompletedTestSerializer(serializers.ModelSerializer):
    # questions = CompletedQuestionSerializer()
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = ['id', 'title', 'questions']
    
    def get_questions(self, obj):
        questions = Question.objects.filter(test=obj)
        return CurrentQuestionSerializer(questions, many=True).data

class CompletedTestSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    tests = CompletedTestSerializer(many=True)

    class Meta:
        model = CompletedTest
        fields = ['id', 'completed_date', 'completed_time', 'user', 'product', 'tests']

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "email": obj.user.email
        }

    def get_product(self, obj):
        return {
            "id": obj.product.id,
            "title": obj.product.title
        }


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
