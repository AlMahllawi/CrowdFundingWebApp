from django.shortcuts import render

def index(request):
    return render(request, 'auth/index.html', { 'pagetitle': "Authentication" })
