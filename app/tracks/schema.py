""" This file defines the graphql schema specific to the tracks functions of
    the app. The rest of the application's schema is tied together in the
    app/app/schema.py file
    """
import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.db.models import Q

from .models import Track, Like
from users.schema import UserType

class TrackType(DjangoObjectType):
    """ A class that defines a type based after our track table model
        required for querying this item.
    """
    class Meta:
        model = Track

class LikeType(DjangoObjectType):
    class Meta:
        model = Like


class Query(graphene.ObjectType):
    tracks = graphene.List(TrackType, search=graphene.String())
    likes = graphene.List(LikeType)

    def resolve_tracks(self, info, search=None):
        if search:
            # use a django Q object for more complex searching
            filter = (
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(url__icontains=search) |
                # we can even go into the nested fields:
                Q(posted_by__username__icontains=search)
            )
            # uses djangos filter arguments to match the search with the track
            # titles. consider the different matchtypes,
            # case insensitive contains is the most general
            return Track.objects.filter(filter)

        return Track.objects.all()

    def resolve_likes(self, info):
        return Like.objects.all()

class CreateTrack(graphene.Mutation):
    track = graphene.Field(TrackType)

    class Arguments:
        title = graphene.String()
        description = graphene.String()
        url = graphene.String()

    def mutate(self, info, **kwargs):
        user = info.context.user  # Associates track with the the user

        if user.is_anonymous:
            raise GraphQLError("Log in to add a track")
        track = Track(title=kwargs.get('title'),
                      description=kwargs.get('description'),
                      url=kwargs.get('url'),
                      posted_by=user)
        track.save()
        return CreateTrack(track=track)

class UpdateTrack(graphene.Mutation):
    track = graphene.Field(TrackType)

    class Arguments:
        """Here we want the original fields of CreateTrack, plus the ID
        """
        track_id = graphene.Int(required=True)
        title = graphene.String()
        description = graphene.String()
        url = graphene.String()

    def mutate(self, info, track_id, title, url, description):
        user = info.context.user
        track = Track.objects.get(id=track_id)
        
        if track.posted_by != user:
            raise GraphQLError("Not permitted to update this track.")
        ("Not permitted to update this track.")

        track.title = title
        track.description = description
        track.url = url

        track.save()

        return UpdateTrack(track=track)

class DeleteTrack(graphene.Mutation):
    track_id = graphene.Int()  # we only need to return the id of the deleted track

    class Arguments:
       track_id = graphene.Int(required=True) 

    def mutate(self, info, track_id):
        user = info.context.user
        track = Track.objects.get(id=track_id)

        if track.posted_by != user:
            raise GraphQLError("Not permitted to delete this track")

        track.delete()

        return DeleteTrack(track_id=track_id)

class CreateLike(graphene.Mutation):
    user = graphene.Field(UserType)
    track = graphene.Field(TrackType)

    class Arguments:
        track_id = graphene.Int(required=True)

    def mutate(self, info, track_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Login to like the track")

        track = Track.objects.get(id=track_id)
        if not track:
            raise GraphQLError("Cannot find a track with given track id")

        Like.objects.create(
            user=user,
            track=track
        )
        return CreateLike(user=user,track=track)

class Mutation(graphene.ObjectType):
    create_track = CreateTrack.Field()
    update_track = UpdateTrack.Field()
    delete_track = DeleteTrack.Field()
    create_like = CreateLike.Field()
