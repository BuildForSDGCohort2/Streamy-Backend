from django.contrib.auth import get_user_model
import graphene
from graphene_django import DjangoObjectType


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()


class Query(graphene.ObjectType):
    users = graphene.Field(UserType)

    def resolve_users(self, info):
        return get_user_model().objects.get()


class CreateUser(graphene.Mutation):
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

        return CreateUser(user=user)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
