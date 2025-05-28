from django.shortcuts import render

# Create your views here.

def index(request):
    context = {
        'page_title': '欢迎来到 NovaCloud', # 示例上下文变量
    }
    return render(request, 'core/index.html', context)
