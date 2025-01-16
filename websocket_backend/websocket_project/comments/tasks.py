from celery import shared_task
from .models import Comments
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from celery.exceptions import MaxRetriesExceededError

@shared_task
def save_comment_task(content, user_id):
    if content == 'error':
        raise Exception({"error": "comment errorrrrr"})
    comment = Comments.objects.create(content=content, user_id=user_id)
    
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'comments',  
        {
            'type': 'send_comment',
            'content': comment.content,
            'user_id': user_id,
            'timestamp': comment.timestamp.isoformat()
        }
    )
    return {'id': comment.id, 'content': comment.content, 'user_id': user_id}



# @shared_task(bind=True, max_retries=5, default_retry_delay=60)
# def save_comment_task(self, content):
#     try:
#         if content == 'error':
#             raise Exception({"error": "comment errors"})
#         comment = Comments.objects.create(content=content)

#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             'comments',
#             {
#                 'type': 'send_comment',
#                 'content': comment.content,
#                 'timestamp': comment.timestamp.isoformat()
#             }
#         )

#         return {'id': id.content, 'content': comment.content}
    
#     except Exception as exc:
#         try:
#             raise self.retry(exc=exc)
        
#         except MaxRetriesExceededError:
#             raise Exception("Comment has exceptioned.")