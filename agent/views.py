from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os
import requests
import logging
from .rag_system import RAGSystem

# 设置日志
logger = logging.getLogger(__name__)

# 初始化RAG系统
rag_system = RAGSystem()

@csrf_exempt  # 暂时关闭 CSRF 保护
def chat_view(request):
    try:
        data = json.loads(request.body)
        message = data.get("message", "")
        
        if not message:
            return JsonResponse({"error": "消息不能为空"}, status=400)
        
        # 从环境变量获取DeepSeek API密钥
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            logger.error("DeepSeek API密钥未设置")
            return JsonResponse({"error": "API配置错误"}, status=500)
        
        # 使用RAG系统获取相关上下文
        context = rag_system.get_context_for_query(message, top_k=3)
        
        # 调用DeepSeek API，传入上下文
        reply = call_deepseek_api_with_context(message, api_key, context)
        
        return JsonResponse({"reply": reply})
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "无效的JSON数据"}, status=400)
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        return JsonResponse({"error": "服务器内部错误"}, status=500)

def call_deepseek_api_with_context(message, api_key, context):
    """
    调用DeepSeek API获取回复，并传入RAG检索的上下文
    """
    try:
        url = "https://api.deepseek.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建系统提示词，包含RAG上下文
        system_prompt = f"""你是一个专业的秋招助手，帮助用户解答关于校园招聘、求职面试、职业规划等问题。

以下是相关的职位信息作为参考：
{context}

请基于以上信息回答用户的问题。如果用户的问题与这些职位信息相关，请结合具体信息给出建议。如果用户的问题与这些职位信息不直接相关，请基于你的专业知识回答。

请用友好、专业的语气回答用户的问题。"""
        
        # 构建请求数据
        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user", 
                    "content": message
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # 提取回复内容
        if 'choices' in result and len(result['choices']) > 0:
            reply = result['choices'][0]['message']['content']
            return reply
        else:
            logger.error(f"DeepSeek API返回格式异常: {result}")
            return "抱歉，我暂时无法处理您的请求，请稍后再试。"
            
    except requests.exceptions.Timeout:
        logger.error("DeepSeek API请求超时")
        return "抱歉，请求超时，请稍后再试。"
    except requests.exceptions.RequestException as e:
        logger.error(f"DeepSeek API请求失败: {str(e)}")
        return "抱歉，服务暂时不可用，请稍后再试。"
    except Exception as e:
        logger.error(f"调用DeepSeek API时出错: {str(e)}")
        return "抱歉，处理您的请求时出现了问题，请稍后再试。"

@csrf_exempt
def rag_test_view(request):
    """
    RAG系统测试接口，用于调试和验证RAG功能
    """
    try:
        data = json.loads(request.body)
        query = data.get("query", "")
        
        if not query:
            return JsonResponse({"error": "查询不能为空"}, status=400)
        
        # 获取相关职位
        relevant_jobs = rag_system.retrieve_relevant_jobs(query, top_k=5)
        
        # 格式化上下文
        context = rag_system.format_context_for_ai(relevant_jobs)
        
        return JsonResponse({
            "query": query,
            "relevant_jobs": relevant_jobs,
            "context": context,
            "total_jobs": len(rag_system.job_data)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "无效的JSON数据"}, status=400)
    except Exception as e:
        logger.error(f"RAG测试时出错: {str(e)}")
        return JsonResponse({"error": "服务器内部错误"}, status=500)
