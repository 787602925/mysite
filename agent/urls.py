from django.urls import path
from .views import chat_view, rag_test_view

urlpatterns = [
    path("chat/", chat_view, name="chat"),
    path("rag-test/", rag_test_view, name="rag_test"),
]
