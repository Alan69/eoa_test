from django.contrib import admin
from .models import Test, Question, Option, Result, BookSuggestion, Product, CompletedTest, CompletedQuestion
from accounts.models import User
from django.contrib import messages

class OptionInline(admin.TabularInline):
    model = Option
    extra = 1


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'test', 'get_product')  # Added 'get_product' to display Product
    search_fields = ('text', 'test__title', 'test__product__title')  # Allow searching by related fields
    list_filter = ('test__product', 'test')  # Add filters for Test and Product
    inlines = [OptionInline]

    def get_product(self, obj):
        """
        Display the Product related to the Question via the Test relationship.
        """
        return obj.test.product.title if obj.test and obj.test.product else 'N/A'

    get_product.short_description = 'Product'  # Set column header in admin


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

    @admin.action(description='Delete Questions with no text')
    def delete_empty_text_questions(self, request, queryset):
        deleted, _ = Question.objects.filter(text__isnull=True).delete()
        messages.success(request, f'Successfully deleted {deleted} question(s) with no text.')

    actions = [delete_empty_text_questions]


class TestAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'number_of_questions', 'score', 'grade', 'date_created', 'product')
    search_fields = ('id', 'title', 'product__title', 'grade')
    list_filter = ('date_created', 'product')
    inlines = [QuestionInline]

class ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'test', 'student', 'score', 'created', 'is_correct')
    search_fields = ('student__username', 'test__title')
    list_filter = ('created', 'is_correct')

class BookSuggestionAdmin(admin.ModelAdmin):
    list_display = ('book_title', 'question')
    search_fields = ('book_title', 'question__text')
    list_filter = ('question',)

admin.site.register(Product)
admin.site.register(Test, TestAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(BookSuggestion, BookSuggestionAdmin)
admin.site.register(CompletedTest)
admin.site.register(CompletedQuestion)
