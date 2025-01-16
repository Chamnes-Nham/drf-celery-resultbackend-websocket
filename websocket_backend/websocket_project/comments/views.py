from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Comments
from rest_framework import status
from rest_framework.response import Response
from .tasks import save_comment_task
from pymongo import MongoClient
from django.http import JsonResponse
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.models import Session
from django.shortcuts import get_object_or_404


class CommentView(APIView):

    def get(self, request, *args, **kwargs):
        comments = Comments.objects.all().order_by("-timestamp")
        comment_list = [
            {
                "id": comment.id,
                "content": comment.content,
                "timestamp": comment.timestamp,
            }
            for comment in comments
        ]
        return Response(comment_list, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        print("Session Key:", request.session.session_key)
        print("User:", request.user)
        print("Is Authenticated:", request.user.is_authenticated)

        session_id = request.session.session_key
        if not session_id:
            return Response(
                {"error": "session_id not found, User not authorizations"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        session = get_object_or_404(Session, session_key=session_id)
        session_data = session.get_decoded()

        user_id = session_data.get("_auth_user_id")
        if not user_id or not request.user.is_authenticated:
            return Response(
                {"error": "User unauthorize!!"}, status=status.HTTP_401_UNAUTHORIZED
            )

        content = request.data.get("content", "")
        if not content:
            return Response(
                {"error": "content is require."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=user_id)

        except User.DoesNotExist:
            return Response(
                {"error": "User not fond"}, status=status.HTTP_404_NOT_FOUND
            )

        task = save_comment_task.delay(content, user.id)
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)

    def delete(self, request):
        user_id = request.query_params.get("user_id")

        if not user_id:
            return Response(
                {"error": "user_id is required as a query parameter!"}, status=400
            )

        try:
            comment = Comments.objects.get(id=user_id)
        except Comments.DoesNotExist:
            return Response(
                {"error": f"Comment with id {user_id} not found!"}, status=404
            )
        comment.delete()
        return Response(
            {"message": f"Comment with id {user_id} has been deleted successfully."},
            status=200,
        )


class ResultBackenListView(APIView):
    def get(self, request):
        client_source = MongoClient("mongodb://localhost:27017/")
        database = client_source["celery_results"]
        collections = database["celery_taskmeta"]

        status_filter = request.query_params.get("status")
        query = {}

        if status_filter:
            query["status"] = status_filter

        tasks_cursor = collections.find(query)
        list_tasks = []

        if status_filter == "SUCCESS":
            total_task = collections.count_documents({"status": "SUCCESS"})
        elif status_filter == "FAILURE":
            total_task = collections.count_documents({"status": "FAILURE"})
        else:
            total_task = collections.count_documents({})

        for task_data in tasks_cursor:
            list_tasks.append(
                {
                    "task_id": task_data.get("_id"),
                    "status": task_data.get("status"),
                    "result": task_data.get("result"),
                }
            )
        return Response(
            {"List_tasks": list_tasks, "total_task": total_task},
            status=status.HTTP_200_OK,
        )


class SigupView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")

        if not username and not password:
            return Response(
                {"error": "username and password are require."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User(username=username)
        user.set_password(password)
        user.email = email
        user.save()
        return Response(
            {"message": f"User {username} has created successfully"},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = request.user

        if not username and not password:
            return Response({"error": "Username and password are require!!!"})

        try:
            user = authenticate(username=username, password=password)

            if user is None:
                return Response(
                    {"error": "Invalid username and password!!!"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            if user.is_authenticated:
                logout(request)
                # request.session.flush()
                request.session.cycle_key()

            login(request, user)
            session_id = request.session.session_key
            response = JsonResponse(
                {"message": f"User: {user.username} login successfully"}
            )
            response.set_cookie("sessionid", session_id, secure=False, httponly=True)
            return response
            # return Response(
            #     {"message": f"{user.username} has loging successfully."},
            #     status=status.HTTP_202_ACCEPTED,
            # )

        except User.DoesNotExist:
            return Response(
                {"error": f"User: {user.username} Not Found"},
                status=status.HTTP_404_NOT_FOUND,
            )


def result_backend_id(request, task_id):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["celery_results"]
    collections = db["celery_taskmeta"]

    task = collections.find_one({"_id": task_id})

    if task:
        result = {
            "task_id": str(task.get("_id")),
            "status": task.get("status"),
            "result": task.get("result"),
        }

    else:
        return JsonResponse(
            {"error": "task not found"}, status=status.HTTP_404_NOT_FOUND
        )

    client.close()

    return JsonResponse(result)


def task_failure(request):
    client_source = MongoClient("mongodb://localhost:27017/")
    database = client_source["celery_results"]
    collections = database["celery_taskmeta"]

    tasks_fail = collections.find({"status": "FAILURE"})
    list_tasks_fail = []
    total_task_failure = collections.count_documents({"status": "FAILURE"})

    for task_data in tasks_fail:
        list_tasks_fail.append(
            {
                "task_id": task_data.get("_id"),
                "status": task_data.get("status"),
                "result": task_data.get("result"),
            }
        )

    client_source.close()
    return JsonResponse(
        {"tasks_failure": list_tasks_fail, "total_task_fail": total_task_failure}
    )


def task_success(request):
    client_source = MongoClient("mongodb://localhost:27017/")
    database = client_source["celery_results"]
    collections = database["celery_taskmeta"]

    task_success = collections.find({"status": "SUCCESS"})
    list_task_success = []
    total_task_success = collections.count_documents({"status": "SUCCESS"})

    for tasks_data in task_success:
        list_task_success.append(
            {
                "task_id": tasks_data.get("_id"),
                "status": tasks_data.get("status"),
                "result": tasks_data.get("result"),
            }
        )

    client_source.close()
    return JsonResponse(
        {"task_success": list_task_success, "total_task_success": total_task_success}
    )
