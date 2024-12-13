import json
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

    # Tổng thu nhập và chi tiêu
    total_income = sum(income_by_month)
    total_expense = sum(expense_by_month)
    balance = total_income - total_expense
    advice = "Hãy tiết kiệm!" if balance < 0 else "Bạn có thể tiết kiệm thêm!"

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