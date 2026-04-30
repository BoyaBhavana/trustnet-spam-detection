from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
import csv

from .models import Analysis
from .ml_model import (
    predict_spam,
    fake_user_score,
    calculate_trust,
    analyze_url_details
)


def home(request):
    if not request.user.is_authenticated:
        return redirect('login')

    data = Analysis.objects.filter(user=request.user)

    total = data.count()
    risky = data.filter(status="Risky").count()
    safe = data.filter(status="Trusted").count()

    return render(request, 'dashboard.html', {
        'total': total,
        'risky': risky,
        'safe': safe
    })


def analyze(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        text = request.POST.get('text', '')
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        url = request.POST.get('url', '')

        spam = predict_spam(text) if text else 0
        fake = fake_user_score(username) if username else 0
        url_data = analyze_url_details(url) if url else {
            "risk": 0,
            "reasons": []
        }

        url_risk = url_data["risk"]

        final_risk = min((spam * 0.4 + fake * 0.3 + url_risk * 0.3) * 100, 100)

        if final_risk <= 30:
            status = "Trusted"
        elif final_risk <= 60:
            status = "Suspicious"
        else:
            status = "Risky"

        reasons = []

        if spam > 0.5:
            reasons.append("Contains spam-like content")

        if fake > 0.3:
            reasons.append("Suspicious username pattern")

        if url_risk > 0:
            reasons.extend(url_data["reasons"])

        Analysis.objects.create(
            user=request.user,
            text=text,
            username=username,
            email=email,
            url=url,
            risk_score=round(final_risk, 2),
            status=status
        )

        return render(request, 'result.html', {
            'text': text,
            'username': username,
            'email': email,
            'url': url,

            'spam': round(spam, 2),
            'fake': round(fake, 2),
            'url_risk': round(url_risk, 2),

            'risk': round(final_risk, 2),
            'status': status,
            'reasons': reasons
        })

    return redirect('home')


def register_view(request):
    form = UserCreationForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('login')

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )

        if user:
            login(request, user)
            return redirect('home')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def history(request):
    if not request.user.is_authenticated:
        return redirect('login')

    data = Analysis.objects.filter(user=request.user).order_by('-created_at')

    labels = [str(d.created_at.date()) for d in data[:5]]
    scores = [d.risk_score for d in data[:5]]

    return render(request, 'history.html', {
        'data': data,
        'labels': labels,
        'scores': scores
    })


def reports(request):
    if not request.user.is_authenticated:
        return redirect('login')

    data = Analysis.objects.filter(user=request.user).order_by('-created_at')

    total = data.count()
    trusted = data.filter(status="Trusted").count()
    suspicious = data.filter(status="Suspicious").count()
    risky = data.filter(status="Risky").count()

    return render(request, 'reports.html', {
        'data': data,
        'total': total,
        'trusted': trusted,
        'suspicious': suspicious,
        'risky': risky
    })


def profile_check(request):
    if not request.user.is_authenticated:
        return redirect('login')

    return render(request, 'profile_check.html')


def api_info(request):
    if not request.user.is_authenticated:
        return redirect('login')

    return render(request, 'api_info.html')


def export_csv(request):
    if not request.user.is_authenticated:
        return redirect('login')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="trustnet_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Text', 'Username', 'Email', 'URL', 'Risk Score', 'Status', 'Date'])

    data = Analysis.objects.filter(user=request.user).order_by('-created_at')

    for d in data:
        writer.writerow([
            d.text,
            d.username,
            d.email,
            d.url,
            d.risk_score,
            d.status,
            d.created_at
        ])

    return response
def get_status(score):
    if score <= 30:
        return "Trusted"
    elif score <= 60:
        return "Suspicious"
    else:
        return "Risky"


def batch_analysis(request):
    if not request.user.is_authenticated:
        return redirect('login')

    results = []

    if request.method == 'POST':
        input1_type = request.POST.get('input1_type')
        input1_value = request.POST.get('input1_value')

        input2_type = request.POST.get('input2_type')
        input2_value = request.POST.get('input2_value')

        input3_type = request.POST.get('input3_type')
        input3_value = request.POST.get('input3_value')

        input4_type = request.POST.get('input4_type')
        input4_value = request.POST.get('input4_value')

        inputs = [
            (input1_type, input1_value),
            (input2_type, input2_value),
            (input3_type, input3_value),
            (input4_type, input4_value),
        ]

        for input_type, value in inputs:
            if not value:
                continue

            risk = 0
            reasons = []

            if input_type == "message":
                spam = predict_spam(value)
                risk = spam * 100
                if spam > 0.5:
                    reasons.append("Message contains spam-like content")

            elif input_type == "username":
                fake = fake_user_score(value)
                risk = fake * 100
                if fake > 0.3:
                    reasons.append("Suspicious username pattern")

            elif input_type == "email":
                fake = fake_user_score(value)
                risk = fake * 100
                if "free" in value.lower() or "win" in value.lower() or "offer" in value.lower():
                    risk += 30
                    reasons.append("Email contains suspicious words")

            elif input_type == "url":
                url_data = analyze_url_details(value)
                risk = url_data["risk"] * 100
                reasons.extend(url_data["reasons"])

            risk = min(round(risk, 2), 100)
            status = get_status(risk)

            results.append({
                "type": input_type,
                "value": value,
                "risk": risk,
                "status": status,
                "reasons": reasons
            })

    return render(request, 'batch_analysis.html', {'results': results})