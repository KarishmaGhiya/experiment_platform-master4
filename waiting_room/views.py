from django.shortcuts import render


# Create your views here.
def wait_home(request):
    return render(request,'waiting_room/wait_home.html')


