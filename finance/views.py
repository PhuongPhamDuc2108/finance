import json
import re
from sklearn.linear_model import LinearRegression
from django.shortcuts import get_object_or_404, render, redirect
import numpy as np
from .forms import IncomeForm, ExpenseForm
from .models import Income, Expense
from django.contrib.auth.decorators import login_required
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from io import BytesIO
import base64
from .forms import UserRegistrationForm
from django.contrib import messages
from django.utils.timezone import now
from django.db.models import Sum
import calendar
from datetime import datetime
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import google.generativeai as genai

def get_financial_summary_text(user):
    """
    Generate a text summary of the user's financial data for speech synthesis.
    """
    # Lấy năm và tháng hiện tại
    current_year = datetime.now().year
    current_month = datetime.now().month
    month_name = calendar.month_name[current_month]

    # Lấy dữ liệu thu nhập và chi tiêu
    incomes = Income.objects.filter(user=user, date__year=current_year)
    expenses = Expense.objects.filter(user=user, date__year=current_year)

    # Tính tổng thu nhập và chi tiêu
    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    # Tính thu nhập và chi tiêu trong tháng hiện tại
    current_month_incomes = incomes.filter(date__month=current_month)
    current_month_expenses = expenses.filter(date__month=current_month)
    current_month_income = current_month_incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    current_month_expense = current_month_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    current_month_balance = current_month_income - current_month_expense

    # Tính thu nhập theo loại
    income_by_category = incomes.values('source').annotate(total=Sum('amount'))
    income_categories_text = ""
    for item in income_by_category:
        source_display = dict(Income.SOURCE_CHOICES).get(item['source'], item['source'])
        income_categories_text += f"{source_display}: {item['total']} đồng. "

    # Tính chi tiêu theo loại
    expense_by_category = expenses.values('category').annotate(total=Sum('amount'))
    expense_categories_text = ""
    for item in expense_by_category:
        category_display = dict(Expense.CATEGORY_CHOICES).get(item['category'], item['category'])
        expense_categories_text += f"{category_display}: {item['total']} đồng. "

    # Tạo lời khuyên
    advice = "Hãy tiết kiệm!" if balance < 0 else "Bạn có thể tiết kiệm thêm!"

    # Tạo văn bản tổng hợp
    summary = f"""
    Báo cáo tài chính của bạn.
    Tổng thu nhập: {total_income} đồng.
    Tổng chi tiêu: {total_expense} đồng.
    Số dư: {balance} đồng.

    Trong tháng {month_name}:
    Thu nhập: {current_month_income} đồng.
    Chi tiêu: {current_month_expense} đồng.
    Số dư tháng này: {current_month_balance} đồng.

    Chi tiết thu nhập theo loại:
    {income_categories_text}

    Chi tiết chi tiêu theo loại:
    {expense_categories_text}

    Lời khuyên: {advice}
    """

    return summary.strip()
# Trang chủ
def home(request):
    return render(request, 'finance/home.html')

# Thêm thu nhập
@login_required
def add_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            return redirect('financial_report')  # Chuyển hướng đến trang báo cáo tài chính
    else:
        form = IncomeForm(initial={'date': now().date()})  # Tự động điền ngày hiện tại
    return render(request, 'finance/add_income.html', {'form': form})

# Thêm chi tiêu
@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('financial_report')  # Sau khi lưu, chuyển hướng đến trang báo cáo tài chính
    else:
        form = ExpenseForm()
    return render(request, 'finance/add_expense.html', {'form': form})

# Báo cáo tài chính

@login_required
def financial_report(request):
    # Lấy năm hiện tại
    current_year = datetime.now().year
    current_month = datetime.now().month

    # Lấy dữ liệu thu nhập theo tháng và nhóm theo loại thu nhập (source)
    incomes = Income.objects.filter(user=request.user, date__year=current_year)
    income_data = incomes.values('source', 'date__month').annotate(total=Sum('amount')).order_by('date__month')

    income_categories = [item['source'] for item in income_data]
    income_totals = [float(item['total']) for item in income_data]  # Chuyển Decimal thành float
    income_by_month = [sum([float(item['total']) for item in income_data if item['date__month'] == month]) for month in range(1, 13)]

    # Lấy dữ liệu chi tiêu theo tháng và nhóm theo danh mục (category)
    expenses = Expense.objects.filter(user=request.user, date__year=current_year)
    expense_data = expenses.values('category', 'date__month').annotate(total=Sum('amount')).order_by('date__month')

    expense_categories = [item['category'] for item in expense_data]
    expense_totals = [float(item['total']) for item in expense_data]  # Chuyển Decimal thành float
    expense_by_month = [sum([float(item['total']) for item in expense_data if item['date__month'] == month]) for month in range(1, 13)]

    # Tính tổng thu nhập và chi tiêu theo từng loại (cho biểu đồ tròn)
    total_income_by_category = incomes.values('source').annotate(total=Sum('amount'))
    total_expense_by_category = expenses.values('category').annotate(total=Sum('amount'))

    income_category_names = [item['source'] for item in total_income_by_category]
    income_category_totals = [float(item['total']) for item in total_income_by_category]

    expense_category_names = [item['category'] for item in total_expense_by_category]
    expense_category_totals = [float(item['total']) for item in total_expense_by_category]

    # Lấy dữ liệu thu nhập và chi tiêu theo ngày trong tháng hiện tại
    daily_income_data = incomes.filter(date__month=current_month).values('date__day').annotate(total=Sum('amount')).order_by('date__day')
    daily_income_days = [item['date__day'] for item in daily_income_data]
    daily_income_totals = [float(item['total']) for item in daily_income_data]

    daily_expense_data = expenses.filter(date__month=current_month).values('date__day').annotate(total=Sum('amount')).order_by('date__day')
    daily_expense_days = [item['date__day'] for item in daily_expense_data]
    daily_expense_totals = [float(item['total']) for item in daily_expense_data]

    # Tổng thu nhập và chi tiêu
    total_income = sum(income_by_month)
    total_expense = sum(expense_by_month)
    balance = total_income - total_expense
    advice = "Hãy tiết kiệm!" if balance < 0 else "Bạn có thể tiết kiệm thêm!"

    # Tạo văn bản tổng hợp cho text-to-speech
    financial_summary = get_financial_summary_text(request.user)

    # Truyền dữ liệu vào template
    context = {
        'months': json.dumps([calendar.month_name[m] for m in range(1, 13)]),  # Tên tháng (January, February, ...)
        'income_values': json.dumps(income_by_month),
        'expense_values': json.dumps(expense_by_month),
        'income_categories': json.dumps(income_category_names),
        'income_totals': json.dumps(income_category_totals),
        'expense_categories': json.dumps(expense_category_names),
        'expense_totals': json.dumps(expense_category_totals),
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'advice': advice,
        'incomes': incomes,  # Truyền dữ liệu thu nhập vào template
        'expenses': expenses,  # Truyền dữ liệu chi tiêu vào template
        'daily_income_days': json.dumps(daily_income_days),
        'daily_income_totals': json.dumps(daily_income_totals),
        'daily_expense_days': json.dumps(daily_expense_days),
        'daily_expense_totals': json.dumps(daily_expense_totals),
        'financial_summary': json.dumps(financial_summary),  # Thêm văn bản tổng hợp cho text-to-speech
    }

    return render(request, 'finance/financial_report.html', context)


@login_required
def forecast_finance(request):
    # Lấy năm hiện tại
    current_year = datetime.now().year

    # Tổng hợp thu nhập theo tháng
    income_by_month = (
        Income.objects.filter(user=request.user, date__year=current_year)
        .values_list('date__month')
        .annotate(total=Sum('amount'))
        .order_by('date__month')
    )
    income_data = {month: float(total) for month, total in income_by_month}

    # Tổng hợp chi tiêu theo tháng
    expense_by_month = (
        Expense.objects.filter(user=request.user, date__year=current_year)
        .values_list('date__month')
        .annotate(total=Sum('amount'))
        .order_by('date__month')
    )
    expense_data = {month: float(total) for month, total in expense_by_month}

    # Tạo dữ liệu cho biểu đồ
    months = list(range(1, 13))  
    income_values = [income_data.get(month, 0) for month in months]
    expense_values = [expense_data.get(month, 0) for month in months]

    # Dự báo thu nhập và chi tiêu sử dụng hồi quy tuyến tính (AI)
    df = pd.DataFrame({
        'month': months,
        'income': income_values,
        'expense': expense_values
    })

    # Sử dụng LinearRegression để dự đoán
    X = df[['month']]  
    y_income = df['income']
    y_expense = df['expense']

    # Tạo mô hình hồi quy tuyến tính cho thu nhập và chi tiêu
    model_income = LinearRegression()
    model_expense = LinearRegression()

    # Huấn luyện mô hình
    model_income.fit(X, y_income)
    model_expense.fit(X, y_expense)

    # Dự đoán thu nhập và chi tiêu trong năm tiếp theo (Tháng 1 đến tháng 12)
    future_months = np.array(range(1, 13)).reshape(-1, 1)  
    predicted_income = model_income.predict(future_months)
    predicted_expense = model_expense.predict(future_months)

    # Dự báo và lời khuyên
    total_income = sum(income_values)
    total_expense = sum(expense_values)
    balance = total_income - total_expense
    advice = "Hãy tiết kiệm!" if balance < 0 else "Bạn có thể tiết kiệm thêm!"

    # Dự đoán xu hướng
    future_balance = sum(predicted_income) - sum(predicted_expense)
    if future_balance < 0:
        future_advice = "Dự báo tài chính cho thấy bạn cần phải điều chỉnh chi tiêu để tránh thâm hụt!"
    else:
        future_advice = "Dự báo tài chính cho thấy bạn có thể tiết kiệm thêm, tuy nhiên, cần theo dõi chi tiêu chặt chẽ."

    # Kết luận dựa trên dự báo
    if future_balance < 0:
        conclusion = "Cần điều chỉnh chi tiêu và tập trung vào tiết kiệm để tránh tình trạng thâm hụt trong năm tới."
    else:
        conclusion = "Tình hình tài chính ổn định, nhưng vẫn nên tiếp tục theo dõi và điều chỉnh để tối đa hóa tiết kiệm."

    # Truyền dữ liệu vào template
    context = {
        'months': json.dumps([calendar.month_abbr[m] for m in months]),  # Tên tháng (Jan, Feb, ...)
        'income_values': json.dumps(income_values),
        'expense_values': json.dumps(expense_values),
        'predicted_income': json.dumps(predicted_income.tolist()),
        'predicted_expense': json.dumps(predicted_expense.tolist()),
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'advice': advice,
        'future_advice': future_advice,
        'conclusion': conclusion,  # Truyền câu kết luận vào context
    }

    return render(request, 'finance/forecast_finance.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Tài khoản {username} đã được tạo thành công! Bạn có thể đăng nhập.')
            return redirect('login')  
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def delete_income(request, income_id):
    income = get_object_or_404(Income, pk=income_id)
    income.delete()
    return redirect('financial_report')  

# Xóa chi tiêu
@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, pk=expense_id)
    expense.delete()
    return redirect('financial_report') 

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Sau khi đăng nhập thành công, chuyển hướng về trang home
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


@login_required
def account_settings(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your account has been updated!')

            if request.is_ajax():
                return JsonResponse({
                    'success': True,
                    'message': 'Your account has been updated!',
                    'image_url': profile.image.url
                })
            return redirect('account_settings')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'finance/account_settings.html', context)

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import random

def generate_simple_response(user_input, financial_data, profile):
    """
    Generate a simple response when the AI model fails.
    This is a fallback mechanism to ensure the chat always works.
    """
    # Convert user input to lowercase for easier matching
    user_input_lower = user_input.lower()

    # Get financial data
    total_income = financial_data.get('total_income', 'không có thông tin')
    total_expense = financial_data.get('total_expense', 'không có thông tin')
    balance = financial_data.get('balance', 'không có thông tin')

    # Define some common responses
    greetings = ["Xin chào", "Chào bạn", "Rất vui được gặp bạn"]

    # Check for common questions and provide appropriate responses
    if any(word in user_input_lower for word in ["xin chào", "chào", "hello", "hi"]):
        response = f"{random.choice(greetings)}! Tôi là trợ lý tài chính của bạn. Tôi có thể giúp gì cho bạn?"

    elif any(word in user_input_lower for word in ["thu nhập", "kiếm được", "lương"]):
        response = f"Tổng thu nhập của bạn là {total_income}. Bạn có thể xem chi tiết trong báo cáo tài chính."

    elif any(word in user_input_lower for word in ["chi tiêu", "chi phí", "tốn"]):
        response = f"Tổng chi tiêu của bạn là {total_expense}. Bạn có thể xem chi tiết trong báo cáo tài chính."

    elif any(word in user_input_lower for word in ["số dư", "còn lại", "balance"]):
        response = f"Số dư tài khoản của bạn là {balance}."

    elif any(word in user_input_lower for word in ["tiết kiệm", "save", "saving"]):
        if isinstance(balance, (int, float)) and balance > 0:
            response = "Bạn đang có số dư dương, đây là dấu hiệu tốt. Hãy tiếp tục tiết kiệm!"
        else:
            response = "Để tiết kiệm hiệu quả, bạn nên giảm các khoản chi tiêu không cần thiết và lập kế hoạch tài chính hàng tháng."

    elif any(word in user_input_lower for word in ["đầu tư", "invest", "investment"]):
        response = "Đầu tư là cách tốt để tăng trưởng tài sản. Bạn nên tìm hiểu về các loại hình đầu tư phù hợp với mục tiêu tài chính của mình."

    elif any(word in user_input_lower for word in ["mục tiêu", "kế hoạch", "goal", "plan"]):
        response = "Lập kế hoạch tài chính rõ ràng sẽ giúp bạn đạt được mục tiêu. Hãy xác định mục tiêu ngắn hạn và dài hạn, sau đó phân bổ ngân sách phù hợp."

    else:
        # Default response if no specific pattern is matched
        responses = [
            "Tôi không thể trả lời câu hỏi đó chi tiết. Hãy thử hỏi về thu nhập, chi tiêu hoặc số dư của bạn.",
            "Xin lỗi, tôi không hiểu câu hỏi. Bạn có thể hỏi về tình hình tài chính của mình không?",
            "Tôi chỉ có thể giúp bạn với các câu hỏi liên quan đến tài chính cá nhân.",
            "Hệ thống AI đang được nâng cấp. Vui lòng hỏi câu đơn giản hơn về tài chính của bạn."
        ]
        response = random.choice(responses)

    return JsonResponse({"response": response})

@csrf_exempt
@require_POST
def ask_gemini(request):
    try:
        data = json.loads(request.body)
        user_input = data.get("message", "")
        financial_data = data.get("financial_data", {})

        # Lấy thông tin người dùng và giao dịch tài chính gần đây
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            # Create a default profile if it doesn't exist
            profile = Profile.objects.create(user=request.user)

        incomes = Income.objects.filter(user=request.user).order_by('-date')[:5]
        expenses = Expense.objects.filter(user=request.user).order_by('-date')[:5]

        income_transactions = ', '.join([f'{i.source}: {i.amount}' for i in incomes[:3]])
        expense_transactions = ', '.join([f'{expense.category}: {expense.amount}' for expense in expenses[:3]])

        # Chuẩn bị ngữ cảnh cho AI - ngắn gọn hơn
        context = f"""
                Financial context: Income {financial_data.get('total_income', 'N/A')}, Expenses {financial_data.get('total_expense', 'N/A')}, Balance {financial_data.get('balance', 'N/A')}. 
                User is {profile.age or 'unknown age'} years old, working as {profile.occupation or 'unknown occupation'}.
                Recent transactions: {income_transactions}; {expense_transactions}.

                Question: {user_input}

                Provide a brief, direct answer in 1-3 sentences. Focus only on answering the question without unnecessary explanations.
        """
        try:
            # Sử dụng mô hình từ Hugging Face
            model_name = "facebook/blenderbot-400M-distill"  # Mô hình nhỏ, phù hợp cho trò chuyện ngắn gọn
            fallback_models = [
                "facebook/blenderbot-400M-distill",  # Try the same model again
                "facebook/blenderbot-1B-distill",    # Try a larger model
                "facebook/blenderbot_small-90M"      # Try a smaller model as last resort
            ]

            # Kiểm tra xem có cache cho model và tokenizer không
            if not hasattr(ask_gemini, 'model') or not hasattr(ask_gemini, 'tokenizer'):
                try:
                    # Try each model in the fallback list until one works
                    success = False

                    for fallback_model in fallback_models:
                        try:
                            print(f"Attempting to load model: {fallback_model}")

                            # Try to load the tokenizer
                            ask_gemini.tokenizer = AutoTokenizer.from_pretrained(
                                fallback_model,
                                local_files_only=False,  # Allow downloading if not found locally
                                use_fast=True  # Use fast tokenizer if available
                            )

                            # Try to load the model
                            ask_gemini.model = AutoModelForCausalLM.from_pretrained(
                                fallback_model,
                                local_files_only=False,  # Allow downloading if not found locally
                                low_cpu_mem_usage=True  # Optimize for low memory usage
                            )

                            # If we get here, both tokenizer and model loaded successfully
                            model_name = fallback_model
                            success = True
                            print(f"Successfully loaded model: {fallback_model}")
                            break

                        except Exception as model_error:
                            print(f"Error loading model {fallback_model}: {str(model_error)}")
                            continue  # Try the next model

                    # If all models failed, use the simple response generator
                    if not success:
                        print("All models failed to load. Using simple response generator.")
                        return generate_simple_response(user_input, financial_data, profile)

                except Exception as model_error:
                    print(f"Error in model loading process: {str(model_error)}")
                    # Fallback to simple response generation
                    return generate_simple_response(user_input, financial_data, profile)

            try:
                # Tạo input cho model
                inputs = ask_gemini.tokenizer(context, return_tensors="pt", truncation=True, max_length=512)

                # Tạo output từ model với timeout
                import threading
                import queue

                def generate_with_timeout():
                    try:
                        with torch.no_grad():
                            result = ask_gemini.model.generate(
                                inputs.input_ids,
                                max_length=100,  # Giảm độ dài output để tăng tốc
                                num_return_sequences=1,
                                temperature=0.7,  # Giảm temperature để có câu trả lời tập trung hơn
                                top_k=50,
                                top_p=0.9,
                                do_sample=True
                            )
                        result_queue.put(result)
                    except Exception as e:
                        result_queue.put(e)

                # Sử dụng queue để lấy kết quả từ thread
                result_queue = queue.Queue()
                generation_thread = threading.Thread(target=generate_with_timeout)
                generation_thread.daemon = True
                generation_thread.start()

                # Đợi kết quả với timeout
                try:
                    outputs = result_queue.get(timeout=10)  # 10 giây timeout
                    if isinstance(outputs, Exception):
                        raise outputs  # Re-raise exception if that's what we got
                except queue.Empty:
                    print("Model generation timed out")
                    return generate_simple_response(user_input, financial_data, profile)
                except Exception as timeout_error:
                    print(f"Error during model generation: {str(timeout_error)}")
                    return generate_simple_response(user_input, financial_data, profile)

                # Decode output
                reply = ask_gemini.tokenizer.decode(outputs[0], skip_special_tokens=True)

                # Làm sạch và định dạng câu trả lời
                reply = reply.replace(context, "").strip()

                # Nếu câu trả lời quá dài, cắt ngắn lại
                if len(reply.split()) > 100:
                    sentences = reply.split('. ')
                    reply = '. '.join(sentences[:3]) + ('.' if not sentences[2].endswith('.') else '')

                return JsonResponse({"response": reply})
            except Exception as gen_error:
                print(f"Error generating response: {str(gen_error)}")
                # Fallback to simple response generation
                return generate_simple_response(user_input, financial_data, profile)

        except torch.cuda.OutOfMemoryError:
            print("CUDA out of memory error")
            # Fallback to simple response generation
            return generate_simple_response(user_input, financial_data, profile)
        except RuntimeError as rt_error:
            print(f"Runtime error: {str(rt_error)}")
            # Fallback to simple response generation
            return generate_simple_response(user_input, financial_data, profile)

    except Exception as e:
        print(f"Error in ask_gemini: {str(e)}")
        return JsonResponse({"response": f"Lỗi: {str(e)}"}, status=500)

@csrf_exempt
def chat_health_check(request):
    """
    A simple health check endpoint for the chat functionality.
    This can be used to verify if the chat is working correctly.
    """
    try:
        # Check if we can import the required libraries
        import torch
        from transformers import AutoTokenizer

        # Return a success response
        return JsonResponse({
            "status": "ok",
            "message": "Chat service is operational",
            "torch_version": torch.__version__,
            "transformers_available": True
        })
    except Exception as e:
        # Return an error response
        return JsonResponse({
            "status": "error",
            "message": f"Chat service is experiencing issues: {str(e)}",
            "error": str(e)
        }, status=500)

@csrf_exempt
@require_POST
def process_voice_command(request):
    try:
        data = json.loads(request.body)
        command = data.get("command", "").lower()

        # Check for direct income/expense commands with amount
        income_match = re.search(r'thêm thu nhập\s+(.+?)\s+(\d+)', command)
        expense_match = re.search(r'thêm chi tiêu\s+(.+?)\s+(\d+)', command)

        # Check for delete commands
        delete_income_match = re.search(r'xóa thu nhập\s+(\d+)', command)
        delete_expense_match = re.search(r'xóa chi tiêu\s+(\d+)', command)
        delete_last_income_match = re.search(r'xóa khoản thu nhập (cuối cùng|gần nhất|mới nhất)', command)
        delete_last_expense_match = re.search(r'xóa khoản chi tiêu (cuối cùng|gần nhất|mới nhất)', command)

        if income_match:
            # Extract source and amount from the command
            source_text = income_match.group(1).strip()
            amount = int(income_match.group(2))

            # Map the source text to one of the predefined sources
            source = 'Other'  # Default
            if 'lương' in source_text:
                source = 'Salary'
            elif 'kinh doanh' in source_text:
                source = 'Business'
            elif 'đầu tư' in source_text:
                source = 'Investment'

            # Create and save the income
            income = Income(
                user=request.user,
                amount=amount,
                source=source,
                date=now().date()
            )
            income.save()

            return JsonResponse({
                "success": True,
                "message": f"Đã thêm khoản thu nhập {source_text} với số tiền {amount}",
                "action": "income_added",
                "data": {
                    "source": source,
                    "amount": amount,
                    "date": now().date().isoformat()
                }
            })

        elif expense_match:
            # Extract category and amount from the command
            category_text = expense_match.group(1).strip()
            amount = int(expense_match.group(2))

            # Map the category text to one of the predefined categories
            category = 'Other'  # Default
            if 'thực phẩm' in category_text or 'ăn' in category_text:
                category = 'Food'
            elif 'giáo dục' in category_text or 'học' in category_text:
                category = 'Education'
            elif 'giải trí' in category_text:
                category = 'Entertainment'
            elif 'di chuyển' in category_text or 'xe' in category_text:
                category = 'Transport'

            # Create and save the expense
            expense = Expense(
                user=request.user,
                amount=amount,
                category=category,
                date=now().date()
            )
            expense.save()

            return JsonResponse({
                "success": True,
                "message": f"Đã thêm khoản chi tiêu {category_text} với số tiền {amount}",
                "action": "expense_added",
                "data": {
                    "category": category,
                    "amount": amount,
                    "date": now().date().isoformat()
                }
            })

        # Handle delete income by ID
        elif delete_income_match:
            income_id = int(delete_income_match.group(1))
            try:
                income = get_object_or_404(Income, pk=income_id, user=request.user)
                source = income.source
                amount = income.amount
                income.delete()
                return JsonResponse({
                    "success": True,
                    "message": f"Đã xóa khoản thu nhập {source} với số tiền {amount}",
                    "action": "income_deleted",
                    "data": {
                        "id": income_id
                    }
                })
            except Exception as e:
                return JsonResponse({
                    "success": False,
                    "message": f"Không thể xóa khoản thu nhập với ID {income_id}: {str(e)}",
                    "action": "error"
                })

        # Handle delete expense by ID
        elif delete_expense_match:
            expense_id = int(delete_expense_match.group(1))
            try:
                expense = get_object_or_404(Expense, pk=expense_id, user=request.user)
                category = expense.category
                amount = expense.amount
                expense.delete()
                return JsonResponse({
                    "success": True,
                    "message": f"Đã xóa khoản chi tiêu {category} với số tiền {amount}",
                    "action": "expense_deleted",
                    "data": {
                        "id": expense_id
                    }
                })
            except Exception as e:
                return JsonResponse({
                    "success": False,
                    "message": f"Không thể xóa khoản chi tiêu với ID {expense_id}: {str(e)}",
                    "action": "error"
                })

        # Handle delete last income
        elif delete_last_income_match:
            try:
                # Get the most recent income
                income = Income.objects.filter(user=request.user).order_by('-date', '-id').first()
                if income:
                    source = income.source
                    amount = income.amount
                    income_id = income.id
                    income.delete()
                    return JsonResponse({
                        "success": True,
                        "message": f"Đã xóa khoản thu nhập gần nhất: {source} với số tiền {amount}",
                        "action": "income_deleted",
                        "data": {
                            "id": income_id
                        }
                    })
                else:
                    return JsonResponse({
                        "success": False,
                        "message": "Không tìm thấy khoản thu nhập nào để xóa",
                        "action": "error"
                    })
            except Exception as e:
                return JsonResponse({
                    "success": False,
                    "message": f"Không thể xóa khoản thu nhập gần nhất: {str(e)}",
                    "action": "error"
                })

        # Handle delete last expense
        elif delete_last_expense_match:
            try:
                # Get the most recent expense
                expense = Expense.objects.filter(user=request.user).order_by('-date', '-id').first()
                if expense:
                    category = expense.category
                    amount = expense.amount
                    expense_id = expense.id
                    expense.delete()
                    return JsonResponse({
                        "success": True,
                        "message": f"Đã xóa khoản chi tiêu gần nhất: {category} với số tiền {amount}",
                        "action": "expense_deleted",
                        "data": {
                            "id": expense_id
                        }
                    })
                else:
                    return JsonResponse({
                        "success": False,
                        "message": "Không tìm thấy khoản chi tiêu nào để xóa",
                        "action": "error"
                    })
            except Exception as e:
                return JsonResponse({
                    "success": False,
                    "message": f"Không thể xóa khoản chi tiêu gần nhất: {str(e)}",
                    "action": "error"
                })

        # Check for read financial report command
        elif "đọc báo cáo" in command or "đọc kết quả" in command or "đọc chi tiêu" in command:
            # Get financial summary
            summary = get_financial_summary_text(request.user)
            return JsonResponse({
                "success": True,
                "message": "Đang đọc báo cáo tài chính",
                "action": "read_report",
                "text": summary
            })

        # Handle navigation commands
        elif "thêm thu nhập" in command or "thêm khoản thu" in command:
            return JsonResponse({"action": "navigate", "url": "/add_income"})
        elif "thêm chi tiêu" in command or "thêm khoản chi" in command:
            return JsonResponse({"action": "navigate", "url": "/add_expense"})
        elif "báo cáo" in command or "xem báo cáo" in command:
            return JsonResponse({"action": "navigate", "url": "/financial_report"})
        elif "trang chủ" in command or "về trang chủ" in command:
            return JsonResponse({"action": "navigate", "url": "/"})
        elif "dự báo" in command or "forecast" in command:
            return JsonResponse({"action": "navigate", "url": "/forecast_finance"})
        elif "tài khoản" in command or "account" in command:
            return JsonResponse({"action": "navigate", "url": "/account"})

        # For complex commands, use AI
        return ask_gemini(request)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
