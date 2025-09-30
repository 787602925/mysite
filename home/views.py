from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    cards = [
        {"title": "简历", "url": "/resume/", "desc": "我的在线简历"},
        {"title": "秋招", "url": "/autumn/", "desc": "秋招相关的记录"},
        {"title": "日程", "url": "/schedule/", "desc": "日程安排"}
    ]
    return render(request, "home/index.html", {"cards": cards})
