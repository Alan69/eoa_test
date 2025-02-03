from rest_framework import serializers
from .models import Product, Test, Question, Option, CompletedTest, CompletedQuestion
from django.db.models import Q
from random import sample

# start test
class CurrentOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text', 'img']

class CurrentQuestionSerializer(serializers.ModelSerializer):
    options = CurrentOptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'img', 'task_type', 'options']

class CurrentTestSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = ['id', 'title', 'questions']

    def get_questions(self, obj):
        # Fetch all questions related to the test as a queryset
        all_questions = Question.objects.filter(test=obj)

        # If the number of questions is not 40, return a random selection
        if obj.number_of_questions != 40:
            selected_questions = sample(list(all_questions), min(obj.number_of_questions, all_questions.count()))
            return CurrentQuestionSerializer(selected_questions, many=True).data

        # Initialize lists for selected questions
        selected_questions = []

        # Step 1: Select 25 questions (1–25) with any task_type except 10, 8, and 6
        questions_1_to_25 = list(all_questions.exclude(task_type__in=[10, 8, 6])[:25])
        selected_questions.extend(questions_1_to_25)

        # Step 2: Select 5 questions (26–30) with task_type=10
        questions_task_type_10 = list(all_questions.filter(task_type=10)[:5])
        selected_questions.extend(questions_task_type_10)

        # If there are not enough questions with task_type=10, fill the gaps with random questions
        if len(questions_task_type_10) < 5:
            remaining_questions = all_questions.exclude(id__in=[q.id for q in selected_questions])
            additional_questions = sample(list(remaining_questions), min(5 - len(questions_task_type_10), remaining_questions.count()))
            selected_questions.extend(additional_questions)

        # Step 3: Select 5 questions (31–35) with task_type=8
        questions_task_type_8 = list(all_questions.filter(task_type=8)[:5])
        selected_questions.extend(questions_task_type_8)

        # If there are not enough questions with task_type=8, fill the gaps with random questions
        if len(questions_task_type_8) < 5:
            remaining_questions = all_questions.exclude(id__in=[q.id for q in selected_questions])
            additional_questions = sample(list(remaining_questions), min(5 - len(questions_task_type_8), remaining_questions.count()))
            selected_questions.extend(additional_questions)

        # Step 4: Select 5 questions (36–40) with task_type=6
        questions_task_type_6 = list(all_questions.filter(task_type=6)[:5])
        selected_questions.extend(questions_task_type_6)

        # If there are not enough questions with task_type=6, fill the gaps with random questions
        if len(questions_task_type_6) < 5:
            remaining_questions = all_questions.exclude(id__in=[q.id for q in selected_questions])
            additional_questions = sample(list(remaining_questions), min(5 - len(questions_task_type_6), remaining_questions.count()))
            selected_questions.extend(additional_questions)

        # Step 5: Ensure the list has exactly 40 questions
        if len(selected_questions) < 40:
            remaining_questions = all_questions.exclude(id__in=[q.id for q in selected_questions])
            additional_questions = sample(list(remaining_questions), min(40 - len(selected_questions), remaining_questions.count()))
            selected_questions.extend(additional_questions)

        # Serialize and return the selected questions
        return CurrentQuestionSerializer(selected_questions[:40], many=True).data

# start test end

class CurrentProductSerializer(serializers.ModelSerializer):
    tests = CurrentTestSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'tests']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'sum', 'description', 'time', 'subject_limit', 'product_type']

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['id', 'title', 'is_required', 'grade']

class GradeGroupedTestSerializer(serializers.Serializer):
    grade = serializers.IntegerField()
    tests = TestSerializer(many=True)

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
    product = ProductSerializer()

    correct_answers_count = serializers.SerializerMethodField()

    class Meta:
        model = CompletedTest
        fields = [
            'id', 
            'user', 
            'product', 
            'start_test_time', 
            'correct_answers_count',
            'completed_date',
            'time_spent'
        ]

    # Method to calculate correct answers for the specific test
    def get_correct_answers_count(self, obj):
        return obj.completed_questions.filter(selected_option__is_correct=True).count()

    # Method to calculate incorrect answers for the specific test
    def get_incorrect_answers_count(self, obj):
        return obj.completed_questions.filter(selected_option__is_correct=False).count()

    # Method to calculate total questions for the specific test
    def get_total_question_count(self, obj):
        return obj.completed_questions.count()

    # Method to return subjects with correct/incorrect counts for specific subjects
    def get_subjects(self, obj):
        subjects_stats = {}
        for completed_question in obj.completed_questions.all():
            subject_title = completed_question.question.subject_title
            if subject_title not in subjects_stats:
                subjects_stats[subject_title] = {'correct': 0, 'incorrect': 0}
            
            if completed_question.selected_option and completed_question.selected_option.is_correct:
                subjects_stats[subject_title]['correct'] += 1
            else:
                subjects_stats[subject_title]['incorrect'] += 1
        return [{'subject': k, 'correct': v['correct'], 'incorrect': v['incorrect']} for k, v in subjects_stats.items()]

# Serializer for the options within a question
class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text', 'is_correct']

# Serializer for the questions within a test
class QuestionSerializer(serializers.ModelSerializer):
    # All options for the question, assuming reverse relation is 'options'
    all_options = OptionSerializer(source='question.options', many=True)
    selected_option = OptionSerializer(many=True)

    class Meta:
        model = CompletedQuestion  # Model is CompletedQuestion, not Question
        fields = ['id', 'question_text', 'selected_option', 'all_options']
    
    # Add the text field explicitly by accessing it from the 'question' relation
    question_text = serializers.CharField(source='question.text', read_only=True)

    class Meta:
        model = CompletedQuestion  # Serializer is for CompletedQuestion model
        fields = ['id', 'question_text', 'selected_option', 'all_options']  # Include question_text

# Serializer for tests within the product
class CTestSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()  # Custom method to include questions within a test
    total_correct_by_test = serializers.SerializerMethodField()  # Custom field for total correct answers by test
    total_incorrect_by_test = serializers.SerializerMethodField()  # Custom field for total incorrect answers by test

    class Meta:
        model = Test
        fields = ['id', 'title', 'questions', 'total_correct_by_test', 'total_incorrect_by_test']

    # Custom method to retrieve questions and their selected options for the test
    def get_questions(self, obj):
        completed_questions = CompletedQuestion.objects.filter(test=obj, completed_test=self.context.get('completed_test'))
        return QuestionSerializer(completed_questions, many=True).data

    # Custom method to calculate total correct answers for the test
    def get_total_correct_by_test(self, obj):
        completed_questions = CompletedQuestion.objects.filter(test=obj, completed_test=self.context.get('completed_test'))
        return completed_questions.filter(selected_option__is_correct=True).count()

    # Custom method to calculate total incorrect answers for the test
    def get_total_incorrect_by_test(self, obj):
        completed_test = self.context.get('completed_test')
        # Retrieve completed questions for the given test
        completed_questions = CompletedQuestion.objects.filter(test=obj, completed_test=completed_test)
        # Filter for incorrect answers where selected_option__is_correct is either False or Null
        return completed_questions.filter(Q(selected_option__is_correct=False) | Q(selected_option__is_correct__isnull=True)).count()
    
# Serializer for products
class CProductSerializer(serializers.ModelSerializer):
    tests = serializers.SerializerMethodField()  # Custom method to include tests within a product
    total_correct_by_all_tests = serializers.SerializerMethodField()  # Total correct answers across all tests
    total_incorrect_by_all_tests = serializers.SerializerMethodField()  # Total incorrect answers across all tests
    total_question_count_by_all_tests = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'tests', 'total_correct_by_all_tests', 'total_incorrect_by_all_tests', 'total_question_count_by_all_tests']

    # Custom method to retrieve tests related to the completed test
    def get_tests(self, obj):
        completed_test = self.context.get('completed_test')  # Pass completed_test to the serializer context
        return CTestSerializer(completed_test.tests.all(), many=True, context={'completed_test': completed_test}).data

    # Custom method to calculate total correct answers across all tests
    def get_total_correct_by_all_tests(self, obj):
        completed_test = self.context.get('completed_test')
        return CompletedQuestion.objects.filter(completed_test=completed_test, selected_option__is_correct=True).count()

    # Custom method to calculate total incorrect answers across all tests
    def get_total_incorrect_by_all_tests(self, obj):
        completed_test = self.context.get('completed_test')
        # Filter for incorrect answers where selected_option__is_correct is either False or Null
        return CompletedQuestion.objects.filter(
            completed_test=completed_test
        ).filter(
            Q(selected_option__is_correct=False) | Q(selected_option__is_correct__isnull=True)
        ).count()
    
    def get_total_question_count_by_all_tests(self, obj):
        completed_test = self.context.get('completed_test')
        # Count the total number of completed questions for this test
        return CompletedQuestion.objects.filter(completed_test=completed_test).count()

# Serializer for the completed test
class CCompletedTestSerializer(serializers.ModelSerializer):
    product = CProductSerializer()
    user = serializers.StringRelatedField()  # Display user’s string representation
    start_test_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    completed_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = CompletedTest
        fields = ['id', 'user', 'product', 'start_test_time', 'completed_date']