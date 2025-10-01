from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from .storage import list_items, insert_item, remove_item, update_status, update_item


def index(request: HttpRequest) -> HttpResponse:
    """
    简易秋招面板：记录公司与进度，数据保存在 TinyDB 的 JSON 文件。
    字段：company, position, status, note
    """
    if request.method == 'POST':
        action = request.POST.get('action', 'add')
        if action == 'add':
            company = (request.POST.get('company') or '').strip()
            position = (request.POST.get('position') or '').strip()
            url = (request.POST.get('url') or '').strip()
            status = (request.POST.get('status') or '').strip()
            note = (request.POST.get('note') or '').strip()
            if company:
                insert_item({
                    'company': company,
                    'position': position,
                    'url': url,
                    'status': status or '已投',
                    'note': note,
                })
            return redirect('autumn')

        if action == 'delete':
            doc_id = request.POST.get('doc_id')
            if doc_id and doc_id.isdigit():
                remove_item(int(doc_id))
            return redirect('autumn')

        if action == 'update':
            doc_id = request.POST.get('doc_id')
            new_status = (request.POST.get('status') or '').strip()
            if doc_id and doc_id.isdigit() and new_status:
                update_status(int(doc_id), new_status)
            return redirect('autumn')

        if action == 'edit':
            doc_id = request.POST.get('doc_id')
            if doc_id and doc_id.isdigit():
                fields = {
                    'company': (request.POST.get('company') or '').strip(),
                    'position': (request.POST.get('position') or '').strip(),
                    'url': (request.POST.get('url') or '').strip(),
                    'status': (request.POST.get('status') or '').strip(),
                    'note': request.POST.get('note') or '',  # 不 strip() 以保留换行符
                }
                # 过滤空值以避免覆盖成空字符串（仅在用户确实提交了该字段时更新）
                fields = {k: v for k, v in fields.items() if v != ''}
                if fields:
                    update_item(int(doc_id), fields)
            return redirect('autumn')

    items = list_items()

    return render(request, 'autumn/index.html', {
        'items': items,
        'statuses': ['已投', '笔试', '面试', 'Offer', '淘汰', '待反馈'],
    })

# Create your views here.
