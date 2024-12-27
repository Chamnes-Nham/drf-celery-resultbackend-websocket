from celery import shared_task
from .models import Comments
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@shared_task
def save_comment_task(content):
    if content == 'error':
        raise Exception({"error": "comment error"})
    comment = Comments.objects.create(content=content)
    
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'comments',  
        {
            'type': 'send_comment',
            'content': comment.content,
            'timestamp': comment.timestamp.isoformat()
        }
    )
    return {'id': comment.id, 'content': comment.content}
