from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Test, Question, Option, Result, BookSuggestion, Product
import json
import openai
from django.http import JsonResponse
from django.contrib import messages

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    tests = Test.objects.filter(product=product)
    
    user = request.user
    if user.balance >= product.sum:
        user.balance -= product.sum
        user.save()
        messages.success(request, f"Successfully purchased {product.title}. Balance updated.")
    else:
        messages.error(request, "Insufficient balance to purchase this product.")
        # Optionally, handle redirect or show an error message
    
    return render(request, 'test_logic/product_detail.html', {'product': product, 'tests': tests})

@login_required
def test_detail(request):
    test_ids = request.GET.getlist('pk_list')
    
    # if len(test_ids) < 2 or len(test_ids) > 5:
    #     return render(request, 'error.html', {'message': 'Выберите от 2 до 5 тестов.'})

    tests = Test.objects.filter(pk__in=test_ids)
    questions = Question.objects.filter(test__in=test_ids)

    return render(request, 'test_logic/test_detail.html', {'tests': tests, 'questions': questions})

@login_required
def take_test(request, pk):
    # Fetch the test and associated questions
    test = get_object_or_404(Test, pk=pk)
    questions = Question.objects.filter(test=test)
    
    if request.method == 'POST':
        # Retrieve the existing session data or initialize it
        responses = request.session.get('responses', {})
        score = request.session.get('score', 0)
        correct = request.session.get('correct', 0)
        wrong = request.session.get('wrong', 0)
        
        # Get the question ID and the selected option ID from the POST request
        question_id = request.POST.get('question_id')
        selected_option_id = request.POST.get(f'question_{question_id}')
        
        if selected_option_id:
            # Fetch the selected option and the correct option for the question
            selected_option = get_object_or_404(Option, pk=selected_option_id)
            correct_option = get_object_or_404(Option, question_id=question_id, is_correct=True)
            is_correct = selected_option.is_correct
            
            # Update the responses with the selected option
            responses[question_id] = selected_option_id
            
            # Update score and counters based on whether the answer is correct
            if is_correct:
                score += 1
                correct += 1
            else:
                wrong += 1
        
        # Save the updated session data
        request.session['responses'] = responses
        request.session['score'] = score
        request.session['correct'] = correct
        request.session['wrong'] = wrong
        
        # Check if the test is being submitted
        if 'submit' in request.POST:
            return redirect('test_result', pk=test.pk)
        
        return JsonResponse({'status': 'saved'})
    
    # Handle AJAX request to fetch questions
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        questions_data = []
        for question in questions:
            options = [{'id': option.id, 'text': option.text} for option in question.option_set.all()]
            questions_data.append({'id': question.id, 'text': question.text, 'options': options})
        return JsonResponse({'questions': questions_data})
    
    # Render the test-taking page
    return render(request, 'test_logic/take_test.html', {'test': test, 'questions': questions})


@login_required
def test_result(request, pk):
    test = get_object_or_404(Test, pk=pk)
    responses = request.session.get('responses', {})
    correct = 0
    wrong = 0
    results = []

    for question_id, selected_option_id in responses.items():
        question = get_object_or_404(Question, pk=question_id)
        selected_option = get_object_or_404(Option, pk=selected_option_id)
        correct_option = get_object_or_404(Option, question=question, is_correct=True)
        is_correct = selected_option.is_correct

        if is_correct:
            correct += 1
        else:
            wrong += 1

        book_suggestions = BookSuggestion.objects.filter(question=question)
        results.append({
            'question': question,
            'selected_option': selected_option,
            'correct_option': correct_option,
            'is_correct': is_correct,
            'book_suggestions': book_suggestions
        })

        Result.objects.create(
            test=test, 
            student=request.user, 
            question=question, 
            selected_option=selected_option, 
            is_correct=is_correct,
            score=(correct / len(responses)) * 100 if responses else 0
        )

    score = (correct / len(responses)) * 100 if responses else 0

    return render(request, 'test_logic/index.html', {
        'test': test,
        'results': results,
        'score': score,
        'correct': correct,
        'wrong': wrong
    })

