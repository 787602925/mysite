from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt  # 暂时关闭 CSRF 保护
def chat_view(request):
    data = json.loads(request.body)
    message = data.get("message", "")
    # 暂时先返回固定文本，后面可接 LangChain / OpenAI
    reply = f"你说的是：{message} 吗？我之后可以查查秋招信息帮你回答~"
    return JsonResponse({"reply": reply})
