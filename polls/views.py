from django.shortcuts import render
from django.http import HttpResponse

from .models import *

def index(request):
    questions = list(Question.objects.all())

    ans = questions
    return HttpResponse(ans)