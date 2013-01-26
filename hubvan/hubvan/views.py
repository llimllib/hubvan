from django.shortcuts import render

def index(request):
    # View code here...
    return render(request, 'index.html')

def user(request, user):
    # View code here...
    return render(request, 'user.html', {'user': user})
