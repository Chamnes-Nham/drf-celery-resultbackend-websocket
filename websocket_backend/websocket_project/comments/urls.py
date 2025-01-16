from django.urls import path
from .views import (CommentView,
                    result_backend_id, 
                    task_failure,
                    task_success,
                    ResultBackenListView,
                    SigupView,
                    LoginView
                )

urlpatterns = [
    path("comments/", CommentView.as_view(), name="comments"),
    path("task/<str:task_id>/", result_backend_id, name="result_backent_api"), 
    path("task_failure/", task_failure, name = "task_failure"),
    path("task_success/", task_success, name = "task_success"),
    path("result_backend/", ResultBackenListView.as_view(), name = "result_backend"),
    path("signup/", SigupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login")
]
