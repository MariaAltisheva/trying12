from django.db import transaction
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import (CreateAPIView, ListAPIView,
                                     RetrieveUpdateDestroyAPIView)
from rest_framework.pagination import LimitOffsetPagination

from goals.filters import GoalDateFilter
from goals.models import Goal, GoalCategory, GoalComment
from goals.permissions import IsOwnerOrReadOnly
from goals.serializers import (GoalCategoryCreateSerializer,
                               GoalCategorySerializer,
                               GoalCommentCreateSerializer,
                               GoalCommentSerializer, GoalCreateSerializer,
                               GoalSerializer)


class GoalCategoryCreateView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(ListAPIView):
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategorySerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    # filterset_fields = ['board']

    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title']

    def get_queryset(self):
        return GoalCategory.objects.filter(
            user_id=self.request.user.id,
            is_deleted=False
        )


class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return GoalCategory.objects.filter(
            # board__participants__user_id=self.request.user.id,
            is_deleted=False
        )

    def perform_destroy(self, instance: GoalCategory):
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=('is_deleted',))
            Goal.objects.filter(category=instance).update(status=Goal.Status.archived)
        return instance


class GoalCreateView(CreateAPIView):
    serializer_class = GoalCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class GoalListView(ListAPIView):
    model = Goal
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalSerializer
    filterset_class = GoalDateFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title', 'description']

    def get_queryset(self):
        return Goal.objects.filter(
            user_id=self.request.user.id,
            category__is_deleted=False
        ).exclude(status=Goal.Status.archived)

class GoalView(RetrieveUpdateDestroyAPIView):
    model = Goal
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    # filter_backends = [DjangoFilterBackend, OrderingFilter]
    # filterset_field = ['goal']
    # ordering = ['-created']
    def get_queryset(self):
        return Goal.objects.filter(
            category__is_deleted=False
        ).exclude(status=Goal.Status.archived)
    def perform_destroy(self, instance: Goal):
        instance.status = Goal.Status.archived
        instance.save(update_fields=('status',))
        return instance


class GoalCommentCreateView(CreateAPIView):
    serializer_class = GoalCommentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class GoalCommentListView(ListAPIView):
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [OrderingFilter, SearchFilter]
    filterset_fields = ['goal']
    ordering = ['-created']

    def get_queryset(self):
        return GoalComment.objects.filter(
            user_id=self.request.user.id,
            # goal__category__board__participants__user_id=self.request.user.id
        )
#

class GoalCommentView(RetrieveUpdateDestroyAPIView):
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = GoalCommentSerializer

    def get_queryset(self):
        return GoalComment.objects.filter(
            user_id=self.request.user.id,
            # goal__category__board__participants__user_id=self.request.user.id
        )


# class BoardCreateView(CreateAPIView):
#     permission_classes = [BoardPermissions]
#     serializer_class = BoardCreateSerializer
#
#
# class BoardListView(ListAPIView):
#     model = Board
#     permission_classes = [BoardPermissions]
#     serializer_class = BoardListSerializer
#     ordering = ['title']
#
#     def get_queryset(self):
#         return Board.objects.prefetch_related('participants').filter(
#             participants__user_id=self.request.user.id, is_deleted=False)
#
#
# class BoardView(RetrieveUpdateDestroyAPIView):
#     model = Board
#     permission_classes = [permissions.IsAuthenticated, BoardPermissions]
#     serializer_class = BoardSerializer
#
#     def get_queryset(self):
#         return Board.objects.prefetch_related('participants').filter(
#             participants__user_id=self.request.user.id, is_deleted=False)
#
#     def perform_destroy(self, instance):
#         with transaction.atomic():
#             instance.is_deleted = True
#             instance.save(update_fields=('is_deleted',))
#             instance.categories.update(is_deleted=True)
#             Goal.objects.filter(category__board=instance).update(
#                 status=Goal.Status.archived
#             )
#         return instance
