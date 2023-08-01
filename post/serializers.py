from rest_framework import serializers
from .models import *

class PostSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()

    def get_comments(self, instance):
        comments = Comment.objects.filter(post=instance)
        serializer = CommentSerializer(comments, many=True)
        return serializer.data

    class Meta:
        model = Post
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "comments"]

        

class PostListSerializer(serializers.ModelSerializer):
    comments_cnt = serializers.SerializerMethodField()

    def get_comments_cnt(self, instance):
        return Comment.objects.filter(post=instance).count()

    class Meta:
        model = Post
        fields = ["id", "title", "writer", "content", "updated_at", "created_at", "comments_cnt","likes"]
        read_only_fields = ["id", "created_at", "updated_at", "comments_cnt"]


class CommentSerializer(serializers.ModelSerializer):
    
    post = serializers.SerializerMethodField()
    
    def get_post(self, instance):
        return instance.post.title
    
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['post']