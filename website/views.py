from django.shortcuts import render

# Create your views here.
def home(request):
    print(type(request))
    return render(request, "index.html")