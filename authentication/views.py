from django.shortcuts import render, redirect
from .forms import RegistrationForm

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("home:index")  # بعد التسجيل يرجع للهوم
    else:
        form = RegistrationForm()
    return render(request, "auth/register.html", {"form": form})


