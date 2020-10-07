import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.db.models import Q

from .models import Movie, Like
from users.schema import UserType


class MovieType(DjangoObjectType):
    class Meta:
        model = Movie


class LikeType(DjangoObjectType):
    class Meta:
        model = Like


class Query(graphene.ObjectType):
    movies = graphene.List(MovieType, search=graphene.String())
    likes = graphene.List(LikeType)

    def resolve_movies(self, info, search=None):
        if search:
            filter = Q(title__icontains=search) | Q(description__icontains=search)

            return Movie.objects.filter(filter)
        return Movie.objects.all()

    def resolve_likes(self, info):
        return Like.objects.all()


class CreateMovie(graphene.Mutation):
    movie = graphene.Field(MovieType)

    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String(required=True)
        url = graphene.String(required=True)
        year = graphene.Int(required=True)
        rating = graphene.Int(required=True)
        poster = graphene.String(required=True)
        cover = graphene.String(required=True)
        genre = graphene.List(graphene.String, required=True)

    def mutate(self, info, **kwargs):
        user = info.context.user

        if user.is_anonymous:
            raise GraphQLError("You must be logged in to add movies")

        if user.is_superuser == False:
            raise GraphQLError("Only admin users can add movies")

        movie = Movie(
            title=kwargs.get("title"),
            description=kwargs.get("description"),
            url=kwargs.get("url"),
            year=kwargs.get("year"),
            rating=kwargs.get("rating"),
            poster=kwargs.get("poster"),
            cover=kwargs.get("cover"),
            genre=kwargs.get("genre"),
            posted_by=user,
        )

        movie.save()

        return CreateMovie(movie=movie)


class UpdateMovie(graphene.Mutation):
    movie = graphene.Field(MovieType)

    class Arguments:
        movie_id = graphene.Int(required=True)
        title = graphene.String()
        description = graphene.String()
        url = graphene.String()
        year = graphene.Int()
        rating = graphene.Int()
        poster = graphene.String()
        cover = graphene.String()
        genre = graphene.List(graphene.String)

    def mutate(self, info, **kwargs):
        user = info.context.user
        movie = Movie.objects.get(id=kwargs.get("movie_id"))

        if movie.posted_by != user:
            raise GraphQLError("Not permitted to update movies")

        movie.title = kwargs.get("title") or movie.title
        movie.description = kwargs.get("description") or movie.description
        movie.url = kwargs.get("url") or movie.url
        movie.year = kwargs.get("year") or movie.year
        movie.rating = kwargs.get("rating") or movie.rating
        movie.poster = kwargs.get("poster") or movie.poster
        movie.cover = kwargs.get("cover") or movie.cover
        movie.genre = kwargs.get("genre") or movie.genre

        movie.save()

        return UpdateMovie(movie=movie)


class DeleteMovie(graphene.Mutation):
    movie_id = graphene.Int()

    class Arguments:
        movie_id = graphene.Int(required=True)

    def mutate(self, info, movie_id):
        user = info.context.user
        movie = Movie.objects.get(id=movie_id)

        if movie.posted_by != user:
            raise GraphQLError("Not permitted to delete movies")

        movie.delete()

        return DeleteMovie(movie_id=movie_id)


class CreateLike(graphene.Mutation):
    user = graphene.Field(UserType)
    movie = graphene.Field(MovieType)

    class Arguments:
        movie_id = graphene.Int(required=True)

    def mutate(self, info, movie_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to like movies")

        movie = Movie.objects.get(id=movie_id)
        if not movie:
            raise GraphQLError("Cannot find movie with the given movie id")

        Like.objects.create(user=user, movie=movie)

        return CreateLike(user=user, movie=movie)


class UpdateLike(graphene.Mutation):
    user = graphene.Field(UserType)
    movie = graphene.Field(MovieType)

    class Arguments:
        movie_id = graphene.Int(required=True)

    def mutate(self, info, movie_id):
        user = info.context.user

        if user.is_anonymous:
            raise GraphQLError("You must be logged in to update likes")

        movie = Movie.objects.get(id=movie_id)
        if not movie:
            raise GraphQLError("Cannot find movie with the given movie id")

        like = Like.objects.get(user=user, movie=movie)
        like.delete()

        return UpdateLike(user=user, movie=movie)


class Mutation(graphene.ObjectType):
    create_movie = CreateMovie.Field()
    update_movie = UpdateMovie.Field()
    delete_movie = DeleteMovie.Field()
    create_like = CreateLike.Field()
    update_like = UpdateLike.Field()