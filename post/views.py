from django.shortcuts import render


from rest_framework import viewsets, mixins
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Post, Comment, PostReaction
from .serializers import PostSerializer, CommentSerializer, PostListSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from rest_framework.exceptions import PermissionDenied
from .permissions import IsOwnerOrReadOnly
from rest_framework.decorators import action

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from django.db.models import Count, Q


class PostViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = Post.objects.annotate(
        like_cnt=Count(
            "reactions", filter=Q(reactions__reaction="like"), distinct=True
        ),
        dislike_cnt=Count(
            "reactions", filter=Q(reactions__reaction="dislike"), distinct=True
        )
        
    )
    filter_backends = [SearchFilter]
    search_fields = ["title"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostSerializer
    

    
    def get_permissions(self):
        if self.action in ["update", "destroy", "partial_update"]:
            return [IsAdminUser()]
        elif self.action in ["likes"]:
            return [IsAuthenticated()]
        return []   

    @action(methods=["POST"], detail=True, permission_classes=IsAuthenticated)
    def likes(self, request, pk=None):
        post = self.get_object()
        user = request.user


        if PostReaction.objects.filter(post=post, user=user, reaction="like").exists():
            PostReaction.objects.filter(post=post, user=user, reaction="like").delete()
                
        else:
            PostReaction.objects.create(post=post, user=user, reaction="like")
            
            
        return Response({"return": "조아요성공"})


    
    @action(methods=["POST"], detail=True, permission_classes=IsAuthenticated)
    def dislikes(self, request, pk=None):
        post = self.get_object()
        user = request.user
        # reaction = request.data.get("reaction")

    

        if PostReaction.objects.filter(post=post, user=user, reaction="dislike").exists():
            PostReaction.objects.filter(post=post, user=user, reaction="dislike").delete()
        else:
            PostReaction.objects.update_or_create(post=post, user=user, defaults={"reaction": "dislike"})
        return Response({"return": "시러요성공"})

    
    @action(methods=["GET"], detail=False)
    def top5(self, request):
        queryset = self.get_queryset().order_by("-like_cnt")[:5]
        serializer = PostListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    
    
class CommentViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def get_permissions(self):
        if self.action in ["update", "destroy", "partial_update"]:
            return [IsOwnerOrReadOnly()]
        return []
    
    def get_object(self):
        obj = super().get_object()
        return obj

class PostCommentViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    # queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    # permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        post = self.kwargs.get("post_id")
        queryset = Comment.objects.filter(post_id=post)
        return queryset
    
    
    def create(self, request,post_id=None):
        post = get_object_or_404(Post, id=post_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post)
        return Response(serializer.data)
    
    def get_permissions(self):
        if self.action in ["list", "create"]:
            return [IsAdminUser()]
        return []
    
