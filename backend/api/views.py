from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from djoser.views import UserViewSet as DjoserUserViewSet
from django.core.files.storage import default_storage

from django.contrib.auth import get_user_model

from .serializers import AvatarUpdateSerializer, UserGetSerializer

User = get_user_model()

from django.core.files.storage import default_storage
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from djoser.views import UserViewSet as DjoserUserViewSet

from django.contrib.auth import get_user_model
from .serializers import AvatarUpdateSerializer, UserGetSerializer

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserGetSerializer
    queryset = User.objects.all()

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def update_avatar(self, request):
        user = request.user

        if request.method == "DELETE":
            if user.avatar and user.avatar.name != "users/image.png":
                if hasattr(user.avatar, 'path'):
                    default_storage.delete(user.avatar.path)
                else:
                    user.avatar.delete(save=False)
            user.avatar = None
            user.save()

            return Response({"avatar": None}, status=status.HTTP_204_NO_CONTENT)

        # PUT
        serializer = AvatarUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(user, serializer.validated_data)

        return Response({"avatar": user.avatar.url if user.avatar else None},
                        status=status.HTTP_200_OK)
