from django.shortcuts import render,redirect
from django.contrib.auth import login,authenticate,logout
# Create your views here.

def account_login(request):
    errors = {}
    if request.method == 'POST':
        _email = request.POST.get('email')
        _password = request.POST.get('password')

        user = authenticate(username=_email,password=_password)
        if user:
            login(request,user)
            next_url = request.GET.get('next','')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('/index/')
        else:
            errors['error'] = '用户名密码不正确'
    return render(request,'login.html',{'errors':errors})

def account_logout(request):
    logout(request)
    return redirect('/account/login/')

def index(request):
    return render(request,'index.html')
