import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from graphql import GraphQLError
import graphql_jwt


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()


class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    me = graphene.Field(UserType)

    def resolve_users(self, info):
        return get_user_model().objects.all()

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

    def mutate(self, info, **kwargs):
        first_name = kwargs.get("first_name")
        last_name = kwargs.get("last_name")
        username = kwargs.get("username")
        email = kwargs.get("email")
        password = kwargs.get("password")

        user = get_user_model()(
            first_name=first_name, last_name=last_name, username=username, email=email
        )
        user.set_password(password)
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


class Mutation(graphene.ObjectType):
    register = Register.Field()
    update_account = UpdateAccount.Field()
    delete_account = DeleteAccount.Field()
    password_change = PasswordChange.Field()
    # password_reset = PasswordReset.Field()

    # django-graphql-jwt authentication
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()