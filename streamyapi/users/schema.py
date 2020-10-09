"""Schema to define user operations."""

import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from graphql import GraphQLError
import graphql_jwt

from .mixins import MutationMixin, ObtainJSONWebTokenMixin

UserModel = get_user_model()


class UserType(DjangoObjectType):
    """A class to define the User model."""

    class Meta:
        """Defines the behavior of the class."""

        model = UserModel


class Query(graphene.ObjectType):
    """A class to query every user and a current user.

    ...

    Methods
    -------
    resolve_users(info):
        Gets all registered users

    resolve_me(info):
        Gets infomation about the current user

    """

    users = graphene.List(UserType)
    me = graphene.Field(UserType)

    def resolve_users(self, info):
        """Get all registered users.

        Parameters
        ----------
        info: object
            Reference to meta information about the execution
            of the current GraphQL Query

            access to per-request context which can be used
            to store anything useful for resolving the query.

        Returns
        -------
        users: list
            A list of all users information

        """
        return UserModel.objects.all()

    def resolve_me(self, info):
        """Get infomation about the current user.

        Parameters
        ----------
        info:
            Reference to meta information about the execution
            of the current GraphQL Query

            access to per-request context which can be used
            to store anything useful for resolving the query.

        Returns
        -------
        user: object
            An object of current user information

        Raises
        ------
        GraphQLError:
            If a user is not logged in

        """
        user = info.context.user

        if user.is_anonymous:
            raise GraphQLError("Not logged in!")

        return user


class Register(graphene.Mutation):
    """A class to create a new user.

    Methods
    -------
    mutate(info, **kwargs):
        creates a new registered users

    """

    user = graphene.Field(UserType)

    class Arguments:
        """Class arguments.

        Arguments
        ---------
        first_name: str
            The user's first name

        last_name: str
            The user's last name

        username: str
            The user's username

        email: str
            The user's email

        password: str
            The user's password

        password2: str
            A password confirmation

        """

        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        password2 = graphene.String(required=True)

    def mutate(self, info, **kwargs):
        """Create a new user.

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
        user: object
            An object of created user information

        Raises
        ------
        GraphQLError:
            If email already exists
            If username already exists
            If there is a password mismatch

        """
        first_name = kwargs.get("first_name")
        last_name = kwargs.get("last_name")
        username = kwargs.get("username")
        email = kwargs.get("email")
        password = kwargs.get("password")
        password2 = kwargs.get("password2")

        user = UserModel(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
        )

        if UserModel.objects.filter(email=email).exists():
            raise GraphQLError("Email is already in use!")

        if UserModel.objects.filter(username=username).exists():
            raise GraphQLError("Username is already in use!")

        if password != password2:
            raise GraphQLError("Password mismatch! Please check again")

        user.set_password(password)
        user.set_password(password2)
        user.save()

        return Register(user=user)


class UpdateAccount(graphene.Mutation):
    """A class to update a user information.

    ...

    Methods
    -------
    mutate(info, **kwargs):
        updates a registered users

    """

    user = graphene.Field(UserType)

    class Arguments:
        """Class arguments.

        Arguments
        ---------
        first_name: str (optional)
            The new first name

        last_name: str (optional)
            The new last name

        email: str (optional)
            The new email

        is_superuser: bool (optional)
            The new user type

        """

        # user_id = graphene.Int()
        first_name = graphene.String()
        last_name = graphene.String()
        email = graphene.String()
        is_superuser = graphene.Boolean()

    def mutate(self, info, **kwargs):
        """Update infomation about the current user.

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
        user: object
            An object of user updated information

        Raises
        ------
        GraphQLError:
            If user is not logged in and not a super user

        """
        user = info.context.user

        if user.is_superuser:
            user = UserModel.objects.get(id=user.id)

        if user.is_anonymous and user.is_superuser == False:
            raise GraphQLError("Please login to update account!")

        user.first_name = kwargs.get("first_name") or user.first_name
        user.last_name = kwargs.get("last_name") or user.last_name
        user.email = kwargs.get("email") or user.email
        user.is_superuser = kwargs.get("is_superuser") or user.is_superuser

        user.save()

        return UpdateAccount(user=user)


class DeleteAccount(graphene.Mutation):
    """A class to delete a user account.

    ...

    Methods
    -------
    mutate(info, password):
        deletes the user

    """

    password = graphene.String()

    class Arguments:
        """Class arguments.

        ...

        Arguments
        ---------
        password: str
            The user's current password

        """

        password = graphene.String(required=True)

    def mutate(self, info, password):
        """Delete the current user account.

        Parameters
        ----------
        info:
            Reference to meta information about the execution
            of the current GraphQL Query

            access to per-request context which can be used
            to store anything useful for resolving the query.

        password: str
            The user's current password

        Returns
        -------
        passowrd: str
            A string of password of the deleted user

        Raises
        ------
        GraphQLError:
            If the current password is incorrect

        """
        user = info.context.user

        if not user.check_password(password):
            raise GraphQLError("Please specify correct password to delete account")

        user.delete()

        return DeleteAccount(password=password)


class PasswordChange(graphene.Mutation):
    """A class to change a user's password.

    ...

    Methods
    -------
    mutate(info, **kwargs):
        updates the user's password

    """

    user = graphene.Field(UserType)

    class Arguments:
        """Class arguments.

        Arguments
        ---------
        old_password: str
            The user's current password

        new_password: str
            The user's new password

        cfrm_password: str
            The user's confirmation password

        """

        old_password = graphene.String(required=True)
        new_password = graphene.String(required=True)
        cfrm_password = graphene.String(required=True)

    def mutate(self, info, old_password, new_password, cfrm_password):
        """Change the current user's password.

        Parameters
        ----------
        info:
            Reference to meta information about the execution
            of the current GraphQL Query

            access to per-request context which can be used
            to store anything useful for resolving the query.

        old_password: str
            The user's current password

        new_password: str
            The new password to use

        cfrm_password: str
            A confirmation of the new password

        Returns
        -------
        user: object
            An object of user updated information

        Raises
        ------
        GraphQLError:
            If user is not logged in and not a super user
            If the old (current) password is incorrect
            If there is a password mismatch

        """
        user = info.context.user

        if user.is_anonymous and user.is_superuser == False:
            raise GraphQLError("You must be logged in to change your password")
        else:
            if not user.check_password(old_password):
                raise GraphQLError("Old password is incorrect")

            if new_password != cfrm_password:
                raise GraphQLError("Password mismatch! Please check again")

            user.set_password(new_password)

            user.save()

            return PasswordChange(user=user)


class ObtainJSONWebToken(
    MutationMixin, ObtainJSONWebTokenMixin, graphql_jwt.JSONWebTokenMutation
):
    """Obtain JSON web token for given user.

    Overrides the ObtainJSONWebToken class.
    Allow users to perform login with the email and password fields instead

    ...

    Methods
    -------
    Field(*args, **kwargs):
        creates a JSON web token for given user

    Field(root, info, **kwargs):
        Resolves the generated token

    """

    LOGIN_ALLOWED_FIELDS = ["email", "username"]

    @classmethod
    def Field(cls, *args, **kwargs):
        """Return the JSON web token for given user."""
        cls._meta.arguments.update({"password": graphene.String(required=True)})
        for field in cls.LOGIN_ALLOWED_FIELDS:
            cls._meta.arguments.update({field: graphene.String()})

        return super(graphql_jwt.JSONWebTokenMutation, cls).Field(*args, **kwargs)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        """Return the resolved information."""
        return cls()


class Mutation(graphene.ObjectType):
    """A class of all Mutations."""

    register = Register.Field()
    update_account = UpdateAccount.Field()
    delete_account = DeleteAccount.Field()
    password_change = PasswordChange.Field()
    # password_reset = PasswordReset.Field()

    # django-graphql-jwt authentication
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
