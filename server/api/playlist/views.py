from datetime import datetime, timedelta

from django.db.models import Count, Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.models import Draft, Playlist, PlaylistInteraction, User, VideoOrder
from api.serializers import (
    PlaylistSerializer,
    UserSerializer,
    VideoOrderSerializer,
    VideoSerializer,
)

# ----------------------------------------------------------------------------


@api_view(["GET"])
@permission_classes([AllowAny])
def getPlaylist(request):
    playlistId = request.query_params.get("playlistId")
    playlist = Playlist.objects.get(id=playlistId)
    serializer = PlaylistSerializer(playlist, many=False)
    playlist_data = serializer.data
    author = User.objects.get(id=playlist.authorId.id)
    author_data = UserSerializer(author).data
    playlist_data["authorName"] = (
        author_data["first_name"] + " " + author_data["last_name"]
    )
    playlist_data["authorProfile"] = author_data["profilePicture"]
    playlist_data["isLiked"] = False
    playlist_data["isDisliked"] = False
    playlist_data["isBookmarked"] = False

    if request.user.is_authenticated:
        user = request.user
        playlist_interaction, _ = PlaylistInteraction.objects.get_or_create(
            userId=user, playlistId=playlist
        )
        playlist_data["isLiked"] = playlist_interaction.isLiked
        playlist_data["isDisliked"] = playlist_interaction.isDisliked
        playlist_data["isBookmarked"] = playlist_interaction.isBookmarked

    return Response(playlist_data, status=status.HTTP_200_OK)


# ----------------------------------------------------------------------------


@api_view(["GET"])
@permission_classes([AllowAny])
def search(request):
    query = request.query_params.get("query")
    playlists = Playlist.objects.filter(
        Q(title__icontains=query)
        | Q(authorId__first_name__icontains=query)
        | Q(authorId__last_name__icontains=query)
        | Q(desc__icontains=query)
    )
    serializer = PlaylistSerializer(playlists, many=True)

    for playlist in serializer.data:
        author = User.objects.get(id=playlist["authorId"])
        author_data = UserSerializer(author).data
        video_count = VideoOrder.objects.filter(
            playlistId=playlist["id"]
        ).count()

        playlist["videoCount"] = video_count
        playlist["authorProfile"] = author_data["profilePicture"]
        playlist["authorName"] = (
            author_data["first_name"] + " " + author_data["last_name"]
        )

        playlist["isLiked"] = False
        playlist["isDisliked"] = False
        playlist["isBookmarked"] = False
        playlist["watchCount"] = 0

    if request.user.is_authenticated:
        user = request.user
        for playlist in serializer.data:
            playlist_instance = Playlist.objects.get(id=playlist["id"])
            playlist_interaction, _ = (
                PlaylistInteraction.objects.get_or_create(
                    userId=user, playlistId=playlist_instance
                )
            )
            playlist["isLiked"] = playlist_interaction.isLiked
            playlist["isDisliked"] = playlist_interaction.isDisliked
            playlist["isBookmarked"] = playlist_interaction.isBookmarked
            playlist["watchCount"] = len(playlist_interaction.watched)

    return Response(serializer.data, status=status.HTTP_200_OK)


# ----------------------------------------------------------------------------


@api_view(["GET"])
@permission_classes([AllowAny])
def recommended(request):
    recommended_playlists = []
    if request.user.is_authenticated:
        user = request.user
        liked_playlists = PlaylistInteraction.objects.filter(
            userId=user, isLiked=True
        ).values_list("playlistId", flat=True)
        similar_users = (
            PlaylistInteraction.objects.filter(
                playlistId__in=liked_playlists, isLiked=True
            )
            .values("userId")
            .annotate(common_likes=Count("playlistId"))
            .order_by("-common_likes")[:5]
        )
        recommended_playlists = (
            PlaylistInteraction.objects.filter(
                userId__in=[user["userId"] for user in similar_users],
                isLiked=True,
            )
            .exclude(playlistId__in=liked_playlists)
            .values("playlistId")
            .annotate(likes=Count("userId"))
            .order_by("-likes")[:10]
        )

    if not len(recommended_playlists):
        popular_playlists = Playlist.objects.order_by("-likes")[:10]
        serializer = PlaylistSerializer(popular_playlists, many=True)
    else:
        recommended_playlists = Playlist.objects.filter(
            id__in=[
                playlist["playlistId"] for playlist in recommended_playlists
            ]
        )
        serializer = PlaylistSerializer(recommended_playlists, many=True)

    for playlist in serializer.data:
        if request.user.is_authenticated:
            playlist_id = playlist["id"]
            playlist_instance = Playlist.objects.get(id=playlist_id)
            playlist_interaction, _ = (
                PlaylistInteraction.objects.get_or_create(
                    userId=user, playlistId=playlist_instance
                )
            )
            playlist["isLiked"] = playlist_interaction.isLiked
            playlist["isDisliked"] = playlist_interaction.isDisliked
            playlist["isBookmarked"] = playlist_interaction.isBookmarked
            playlist["watchCount"] = len(playlist_interaction.watched)
        else:
            playlist["isLiked"] = False
            playlist["isDisliked"] = False
            playlist["isBookmarked"] = False
            playlist["watchCount"] = 0

        video_count = VideoOrder.objects.filter(
            playlistId=playlist["id"]
        ).count()
        playlist["videoCount"] = video_count

        author = User.objects.get(id=playlist["authorId"])
        playlist["authorName"] = author.first_name + " " + author.last_name
        playlist["authorProfile"] = author.profilePicture

    return Response(serializer.data, status=status.HTTP_200_OK)


# ----------------------------------------------------------------------------


@api_view(["GET"])
@permission_classes([AllowAny])
def popular(request):
    playlists = Playlist.objects.order_by("-likes")[:10]
    serializer = PlaylistSerializer(playlists, many=True)

    user = None
    if request.user.is_authenticated:
        user = request.user

    for playlist in serializer.data:
        video_count = VideoOrder.objects.filter(
            playlistId=playlist["id"]
        ).count()
        playlist["videoCount"] = video_count

        author = User.objects.get(id=playlist["authorId"])
        playlist["authorName"] = author.first_name + " " + author.last_name
        playlist["authorProfile"] = author.profilePicture

        if user:
            playlist_id = playlist["id"]
            playlist_instance = Playlist.objects.get(id=playlist_id)
            playlist_interaction, _ = (
                PlaylistInteraction.objects.get_or_create(
                    userId=user, playlistId=playlist_instance
                )
            )
            playlist["isLiked"] = playlist_interaction.isLiked
            playlist["isDisliked"] = playlist_interaction.isDisliked
            playlist["isBookmarked"] = playlist_interaction.isBookmarked
            playlist["watchCount"] = len(playlist_interaction.watched)
        else:
            playlist["isLiked"] = False
            playlist["isDisliked"] = False
            playlist["isBookmarked"] = False
            playlist["watchCount"] = 0

    return Response(serializer.data, status=status.HTTP_200_OK)


# ----------------------------------------------------------------------------


@api_view(["GET"])
@permission_classes([AllowAny])
def recent_uploads(request):
    playlists = Playlist.objects.order_by("-created_at")[:10]
    serializer = PlaylistSerializer(playlists, many=True)

    user = None
    if request.user.is_authenticated:
        user = request.user

    for playlist in serializer.data:
        video_count = VideoOrder.objects.filter(
            playlistId=playlist["id"]
        ).count()
        playlist["videoCount"] = video_count

        author = User.objects.get(id=playlist["authorId"])
        playlist["authorName"] = author.first_name + " " + author.last_name
        playlist["authorProfile"] = author.profilePicture

        if user:
            playlist_id = playlist["id"]
            playlist_instance = Playlist.objects.get(id=playlist_id)
            playlist_interaction, _ = (
                PlaylistInteraction.objects.get_or_create(
                    userId=user, playlistId=playlist_instance
                )
            )
            playlist["isLiked"] = playlist_interaction.isLiked
            playlist["isDisliked"] = playlist_interaction.isDisliked
            playlist["isBookmarked"] = playlist_interaction.isBookmarked
            playlist["watchCount"] = len(playlist_interaction.watched)
        else:
            playlist["isLiked"] = False
            playlist["isDisliked"] = False
            playlist["isBookmarked"] = False
            playlist["watchCount"] = 0

    return Response(serializer.data, status=status.HTTP_200_OK)


# ----------------------------------------------------------------------------


@api_view(["GET"])
@permission_classes([AllowAny])
def user_playlists(request):
    user = User.objects.get(username=request.query_params["username"])
    playlists = Playlist.objects.filter(authorId=user)
    serializer = PlaylistSerializer(playlists, many=True)
    for playlist_data in serializer.data:
        author = User.objects.get(id=playlist_data["authorId"])
        playlist_data["authorName"] = (
            author.first_name + " " + author.last_name
        )
        playlist_data["authorProfile"] = author.profilePicture
    return Response(serializer.data, status=status.HTTP_200_OK)


# ----------------------------------------------------------------------------


@api_view(["GET"])
@permission_classes([AllowAny])
def user_liked_playlists(request):
    user = User.objects.get(username=request.query_params["username"])
    playlists = Playlist.objects.filter(
        playlistinteraction__userId=user, playlistinteraction__isLiked=True
    )
    serializer = PlaylistSerializer(playlists, many=True)
    for playlist_data in serializer.data:
        author = User.objects.get(id=playlist_data["authorId"])
        playlist_data["authorName"] = (
            author.first_name + " " + author.last_name
        )
        playlist_data["authorProfile"] = author.profilePicture
    return Response(serializer.data, status=status.HTTP_200_OK)


# ----------------------------------------------------------------------------


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_bookmarked_playlists(request):
    try:
        requested_user_username = request.query_params["username"]
        user = request.user
        if requested_user_username != user.username:
            return Response(
                {"message": "User unauthorized to view this data"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        playlists = Playlist.objects.filter(
            playlistinteraction__userId=user,
            playlistinteraction__isBookmarked=True,
        )
        serializer = PlaylistSerializer(playlists, many=True)
        for playlist_data in serializer.data:
            author = User.objects.get(id=playlist_data["authorId"])
            playlist_data["authorName"] = (
                author.first_name + " " + author.last_name
            )
            playlist_data["authorProfile"] = author.profilePicture
        return Response(serializer.data)
    except Exception:
        return Response(
            {"message": "User not found"}, status=status.HTTP_404_NOT_FOUND
        )


# ----------------------------------------------------------------------------


@api_view(["GET"])
@permission_classes([AllowAny])
def watch_count(request):
    try:
        user = request.user
        playlist_id = request.query_params.get("playlistId")
        playlist = Playlist.objects.get(id=playlist_id)
        playlist_interaction, _ = PlaylistInteraction.objects.get_or_create(
            userId=user, playlistId=playlist
        )
        watch_count = len(playlist_interaction.watched)
        return Response({"watchCount": watch_count}, status=status.HTTP_200_OK)
    except Exception:
        return Response({"watchCount": 0}, status=status.HTTP_200_OK)


# ----------------------------------------------------------------------------


@api_view(["GET"])
@permission_classes([AllowAny])
def getLastWatched(request):
    try:
        user = request.user
        playlist = Playlist.objects.get(id=request.query_params["playlistId"])
        playlist_interaction, _ = PlaylistInteraction.objects.get_or_create(
            userId=user, playlistId=playlist, defaults={"lastWatched": 0}
        )
        return Response(
            {"lastWatched": playlist_interaction.lastWatched},
            status=status.HTTP_200_OK,
        )
    except Playlist.DoesNotExist:
        return Response({"lastWatched": 0}, status=status.HTTP_200_OK)


# ----------------------------------------------------------------------------


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def setLastWatched(request):
    try:
        user = request.user
        playlist_interaction, _ = PlaylistInteraction.objects.get_or_create(
            userId=user,
            playlistId=Playlist.objects.get(id=request.data["playlistId"]),
        )
        playlist_interaction.lastWatched = request.data["lastWatched"]
        playlist_interaction.save()
        return Response(
            {"message": "Last watched updated successfully"},
            stauts=status.HTTP_200_OK,
        )

    except Exception:
        return Response(
            {"message": "Playlist interaction not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


# ----------------------------------------------------------------------------


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def updateWatched(request):
    try:
        user = request.user
        playlist_interaction, _ = PlaylistInteraction.objects.get_or_create(
            userId=user,
            playlistId=Playlist.objects.get(id=request.data["playlistId"]),
        )
        if request.data["add"]:
            if request.data["index"] not in playlist_interaction.watched:
                playlist_interaction.watched.append(request.data["index"])
        else:
            if request.data["index"] in playlist_interaction.watched:
                playlist_interaction.watched.remove(request.data["index"])
        playlist_interaction.save()
        return Response(
            {"message": "Watched updated successfully"},
            status=status.HTTP_200_OK,
        )
    except Exception:
        return Response(
            {"message": "Playlist interaction not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


# ----------------------------------------------------------------------------


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def updateLikeDislike(request):
    try:
        user = request.user
        playlist_interaction, _ = PlaylistInteraction.objects.get_or_create(
            userId=user,
            playlistId=Playlist.objects.get(id=request.data["playlistId"]),
        )
        playlist_interaction.isLiked = request.data["liked"]
        playlist_interaction.isDisliked = request.data["disliked"]
        playlist_interaction.save()

        playlist = Playlist.objects.get(id=request.data["playlistId"])
        playlist.likes += request.data["newLikes"]
        playlist.dislikes += request.data["newDislikes"]
        playlist.save()

        return Response(
            {"message": "Like/Dislike updated successfully"},
            status=status.HTTP_200_OK,
        )
    except Exception:
        return Response(
            {"message": "Playlist interaction not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


# ----------------------------------------------------------------------------


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_playlist(request):
    try:
        user = request.user
        draft_id = request.data["draftId"]
        draft = Draft.objects.get(id=draft_id)
        if draft.authorId.id != user.id:
            return Response(
                {"message": "User unauthorized to create this playlist"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        playlist_data = {
            "title": draft.title,
            "desc": draft.desc,
            "thumbnail": draft.thumbnail,
            "cloudinaryPublicId": draft.cloudinaryPublicId,
            "likes": 0,
            "dislikes": 0,
            "duration": timedelta(0),
            "views": 0,
            "coursePDF": "",
            "authorId": draft.authorId.id,
        }

        playlist_serializer = PlaylistSerializer(data=playlist_data)
        if not playlist_serializer.is_valid():
            return Response(
                playlist_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        playlist = playlist_serializer.save()
        total_duration = timedelta(0)
        selected_videos = [
            video
            for videos in draft.videoList
            for video in videos
            if video["selected"]
        ]

        for index, video in enumerate(selected_videos):
            video_data = video.copy()
            video_data["youtubeHash"] = video["video_id"]
            video_data["duration"] = datetime.strptime(
                video["duration"], "%H:%M:%S"
            ).time()
            del video_data["selected"]
            del video_data["video_id"]

            video_serializer = VideoSerializer(data=video_data)
            if video_serializer.is_valid():
                video = video_serializer.save()
                total_duration += video.duration

                video_order_data = {
                    "index": index,
                    "playlistId": playlist.id,
                    "videoId": video.id,
                }
                video_order_serializer = VideoOrderSerializer(
                    data=video_order_data
                )
                if video_order_serializer.is_valid():
                    video_order_serializer.save()

        playlist.duration = total_duration
        total_seconds = int(total_duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        playlist.save()
        draft.delete()

        return Response(
            {"playlistId": playlist.id}, status=status.HTTP_201_CREATED
        )

    except Draft.DoesNotExist:
        return Response(
            {"message": "Draft not found"}, status=status.HTTP_404_NOT_FOUND
        )

    except Exception:
        return Response(
            {"message": "Error creating playlist"},
            status=status.HTTP_400_BAD_REQUEST,
        )


# ----------------------------------------------------------------------------
