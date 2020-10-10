"""Schema to define movie operations."""

import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.db.models import Q

from .models import Movie, Like
from users.schema import UserType


class MovieType(DjangoObjectType):
    """A class to define the movie model."""

    class Meta:
        """Defines the behavior of the class."""

        model = Movie


class LikeType(DjangoObjectType):
    """A class to define the Like model."""

    class Meta:
        """Defines the behavior of the class."""

        model = Like


class Query(graphene.ObjectType):
    """A class to query all movies and movie likes.

    ...

    Methods
    -------
    resolve_movies(info, search=None):
        Gets all created movies

    resolve_likes(info):
        Gets infomation about the likes on a movie

    """

    movies = graphene.List(MovieType, search=graphene.String())
    likes = graphene.List(LikeType)

    def resolve_movies(self, info, search=None):
        """Get all movies or all searched movies.

        Parameters
        ----------
        info: object
            Reference to meta information about the execution
            of the current GraphQL Query

            access to per-request context which can be used
            to store anything useful for resolving the query.

        search: str (default None)
            search parameter for searching movies

        Returns
        -------
        movies: list
            A list of all movies or all searched movies

        """
        if search:
            filter_by = Q(title__icontains=search)

            return Movie.objects.filter(filter_by)
        return Movie.objects.all()

    def resolve_likes(self, info):
        """Get all likes.

        Parameters
        ----------
        info: object
            Reference to meta information about the execution
            of the current GraphQL Query

            access to per-request context which can be used
            to store anything useful for resolving the query.


        Returns
        -------
        likes: list
            A list of all movie likes

        """
        return Like.objects.all()


class CreateMovie(graphene.Mutation):
    """A class to register a new movie.

    Methods
    -------
    mutate(info, **kwargs):
        creates a new movie

    """

    movie = graphene.Field(MovieType)

    class Arguments:
        """Class arguments.

        Arguments
        ---------
        title: str
            The movie title

        description: str
            The movie description

        url: str
            The movie url

        year: int
            The movie year

        rating: int
            The movie rating

        poster: str
            A movie poster

        cover: str
            A movie cover

        genre: list(str)
            A movie genre

        """

        title = graphene.String(required=True)
        description = graphene.String(required=True)
        url = graphene.String(required=True)
        year = graphene.Int(required=True)
        rating = graphene.Int(required=True)
        poster = graphene.String(required=True)
        cover = graphene.String(required=True)
        genre = graphene.List(graphene.String, required=True)

    def mutate(self, info, **kwargs):
        """Create a new movie.

        Parameters
        ----------
        info:
            Reference to meta information about the execution
            of the current GraphQL Query

            access to per-request context which can be used
            to store anything useful for resolving the query.

        **kwargs: dict
            A dictionary of arguments

        Returns
        -------
        movie: object
            An object of the created movie information

        Raises
        ------
        GraphQLError:
            If user is not logged in
            If user is not a super user

        """
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
    """A class to update movie information.

    ...

    Methods
    -------
    mutate(info, **kwargs):
        updates a specified movie information

    """

    movie = graphene.Field(MovieType)

    class Arguments:
        """Class arguments.

        Arguments
        ---------
        movie_id: int
            The ID of the movie to update

        title: str (optional)
            The movie title

        description: str (optional)
            The movie description

        url: str (optional)
            The movie url

        year: int (optional)
            The movie year

        rating: int (optional)
            The movie rating

        poster: str (optional)
            A movie poster

        cover: str (optional)
            A movie cover

        genre: list(str) (optional)
            A movie genre

        """

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
        """Update infomation about a movie.

        Parameters
        ----------
        info:
            Reference to meta information about the execution
            of the current GraphQL Query

            access to per-request context which can be used
            to store anything useful for resolving the query.

        **kwargs: dict
            A dictionary of arguments

        Returns
        -------
        movie: object
            An object of updated movie information

        Raises
        ------
        GraphQLError:
            If the current user didn't create the movie

        """
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
    """A class to delete a movie.

    ...

    Methods
    -------
    mutate(info, movie_id):
        deletes a movie

    """

    movie_id = graphene.Int()

    class Arguments:
        """Class arguments.

        Arguments
        ---------
        movie_id: int
            The ID of the movie to update

        """

        movie_id = graphene.Int(required=True)

    def mutate(self, info, movie_id):
        """Delete a movie.

        Parameters
        ----------
        info:
            Reference to meta information about the execution
            of the current GraphQL Query

            access to per-request context which can be used
            to store anything useful for resolving the query.

        movie_id: int
            The ID of the movie to delete

        Returns
        -------
        movie_id: int
            The ID of the deleted movie

        Raises
        ------
        GraphQLError:
            If the current user didn't create the movie

        """
        user = info.context.user
        movie = Movie.objects.get(id=movie_id)

        if movie.posted_by != user:
            raise GraphQLError("Not permitted to delete movies")

        movie.delete()

        return DeleteMovie(movie_id=movie_id)


class CreateLike(graphene.Mutation):
    """A class to like a movie.

    ...

    Methods
    -------
    mutate(info, movie_id):
        like a movie

    """

    user = graphene.Field(UserType)
    movie = graphene.Field(MovieType)

    class Arguments:
        """Class arguments.

        Arguments
        ---------
        movie_id: int
            The ID of the movie to like

        """

        movie_id = graphene.Int(required=True)

    def mutate(self, info, movie_id):
        """Likes a specified movie.

        Parameters
        ----------
        info:
            Reference to meta information about the execution
            of the current GraphQL Query

            access to per-request context which can be used
            to store anything useful for resolving the query.

        movie_id: int
            The ID of the movie to like

        Returns
        -------
        user: object
            An object with information who liked the movie

        movie: object
            An object with information on the liked movie

        Raises
        ------
        GraphQLError:
            If the user is not logged in
            If the movie ID does not exist

        """
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to like movies")

        movie = Movie.objects.get(id=movie_id)
        if not movie:
            raise GraphQLError("Cannot find movie with the given movie id")

        Like.objects.create(user=user, movie=movie)

        return CreateLike(user=user, movie=movie)


class UpdateLike(graphene.Mutation):
    """A class to dislike a movie.

    ...

    Methods
    -------
    mutate(info, movie_id):
        updates a movie like

    """

    user = graphene.Field(UserType)
    movie = graphene.Field(MovieType)

    class Arguments:
        """Class arguments.

        Arguments
        ---------
        movie_id: int
            The ID of the movie to dislike

        """

        movie_id = graphene.Int(required=True)

    def mutate(self, info, movie_id):
        """Update Likes on a specified movie.

        Parameters
        ----------
        info:
            Reference to meta information about the execution
            of the current GraphQL Query

            access to per-request context which can be used
            to store anything useful for resolving the query.

        movie_id: int
            The ID of the movie to dislike

        Returns
        -------
        user: object
            An object with information who disliked the movie

        movie: object
            An object with information on the disliked movie

        Raises
        ------
        GraphQLError:
            If the user is not logged in
            If the movie ID does not exist

        """
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
    """A class of all Mutations."""

    create_movie = CreateMovie.Field()
    update_movie = UpdateMovie.Field()
    delete_movie = DeleteMovie.Field()
    create_like = CreateLike.Field()
    update_like = UpdateLike.Field()
