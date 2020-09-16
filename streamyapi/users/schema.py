import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from graphql import GraphQLError
import graphql_jwt

from .mixins import MutationMixin, ObtainJSONWebTokenMixin

UserModel = get_user_model()


class UserType(DjangoObjectType):
    class Meta:
        model = UserModel


class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    me = graphene.Field(UserType)

    def resolve_users(self, info):
        return UserModel.objects.all()

    def resolve_me(self, info):
        user = info.context.user

        if user.is_anonymous:
            raise GraphQLError("Not logged in!")

        return user


class Register(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        password2 = graphene.String(required=True)

    def mutate(self, info, **kwargs):
        first_name = kwargs.get("first_name")
        last_name = kwargs.get("last_name")
        username = kwargs.get("username")
        email = kwargs.get("email")
        password = kwargs.get("password")
        password2 = kwargs.get("password2")

        user = UserModel(
            first_name=first_name, last_name=last_name, username=username, email=email
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
    user = graphene.Field(UserType)

    class Arguments:
        first_name = graphene.String()
        last_name = graphene.String()

    def mutate(self, info, first_name, last_name):
        user = info.context.user

        if user.is_anonymous:
            raise GraphQLError("Please login to update account!")

        if first_name != "":
            user.first_name = first_name

        if last_name != "":
            user.last_name = last_name

        user.save()

        return UpdateAccount(user=user)


class DeleteAccount(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        password = graphene.String(required=True)

    def mutate(self, info, password):
        user = info.context.user

        if not user.check_password(password):
            raise GraphQLError("Please specify correct password to delete account")

        user.delete()

        return DeleteAccount(user=user)


class PasswordChange(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        old_password = graphene.String(required=True)
        new_password = graphene.String(required=True)
        cfrm_password = graphene.String(required=True)

    def mutate(self, info, old_password, new_password, cfrm_password):
        user = info.context.user

        if user.is_anonymous:
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

    LOGIN_ALLOWED_FIELDS = ["email", "username"]

    @classmethod
    def Field(cls, *args, **kwargs):
        cls._meta.arguments.update({"password": graphene.String(required=True)})
        for field in cls.LOGIN_ALLOWED_FIELDS:
            cls._meta.arguments.update({field: graphene.String()})

        return super(graphql_jwt.JSONWebTokenMutation, cls).Field(*args, **kwargs)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls()


class Mutation(graphene.ObjectType):
    register = Register.Field()
    update_account = UpdateAccount.Field()
    delete_account = DeleteAccount.Field()
    password_change = PasswordChange.Field()
    # password_reset = PasswordReset.Field()

    # django-graphql-jwt authentication
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()