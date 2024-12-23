from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Comments
from rest_framework import status
from rest_framework.response import Response
from .tasks import save_comment_task

class CommentView(APIView):

    def get(self, request, *args, **kwargs):
        comments = Comments.objects.all().order_by('-timestamp')
        comment_list = [{"id": comment.id, "content": comment.content, "timestamp": comment.timestamp} for comment in comments]
        return Response(comment_list, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        content = request.data.get("content", "")  # Extract the comment content from the request
        if not content:
            return Response({"error": "Content is required"}, status=status.HTTP_400_BAD_REQUEST)
        task = save_comment_task.delay(content)
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


    def delete(self, request):
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({"error": "user_id is required as a query parameter!"}, status=400)

        try:
            comment = Comments.objects.get(id=user_id)
        except Comments.DoesNotExist:
            return Response({"error": f"Comment with id {user_id} not found!"}, status=404)
        comment.delete()
        return Response({"message": f"Comment with id {user_id} has been deleted successfully."}, status=200)