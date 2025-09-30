from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from pathlib import Path

try:
    from tinydb import TinyDB, Query
except Exception:  # pragma: no cover
    TinyDB = None  # type: ignore
    Query = None  # type: ignore

DB_PATH = Path(__file__).resolve().parent / 'data.json'


def get_db():
    if TinyDB is None:
        raise RuntimeError('TinyDB is not installed. Run: pip install tinydb')
    return TinyDB(DB_PATH)


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
                with get_db() as db:
                    db.insert({
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
                with get_db() as db:
                    db.remove(doc_ids=[int(doc_id)])
            return redirect('autumn')

        if action == 'update':
            doc_id = request.POST.get('doc_id')
            new_status = (request.POST.get('status') or '').strip()
            if doc_id and doc_id.isdigit() and new_status:
                with get_db() as db:
                    db.update({'status': new_status}, doc_ids=[int(doc_id)])
            return redirect('autumn')

    with get_db() as db:
        items = list(db)

    return render(request, 'autumn/index.html', {
        'items': items,
        'statuses': ['已投', '笔试', '面试', 'Offer', '淘汰', '待反馈'],
    })

# Create your views here.
