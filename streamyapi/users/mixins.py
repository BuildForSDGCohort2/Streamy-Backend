from django.contrib.auth import get_user_model
from graphql import GraphQLError

UserModel = get_user_model()


class ObjectDoesNotExist(Exception):
    """The requested object does not exist"""

    silent_variable_failure = True


def get_user_to_login(**kwargs):
    """
    get user by kwargs or secondary email
    to perform login
    raise ObjectDoesNotExist
    """

    try:
        user = UserModel._default_manager.get(**kwargs)
        return user
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist


class MutationMixin:
    """
    All mutations should extend this class
    """

    @classmethod
    def mutate(cls, root, info, **inputs):
        return cls.resolve_mutation(root, info, **inputs)

    @classmethod
    def parent_resolve(cls, root, info, **kwargs):
        return super().mutate(root, info, **kwargs)


class ObtainJSONWebTokenMixin:
    """
    Obtain JSON web token for given user.

    Allow to perform login with different fields,
    and secondary email if set. The fields are
    defined on settings.

    Not verified users can login by default. This
    can be changes on settings.

    If user is archived, make it unarchive and
    return `unarchiving=True` on output.
    """

    LOGIN_ALLOWED_FIELDS = ["email", "password"]

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)

    @classmethod
    def resolve_mutation(cls, root, info, **kwargs):
        if len(kwargs.items()) != 2:
            raise GraphQLError(
                "Must login with password and one of the following fields %s."
                % (cls.LOGIN_ALLOWED_FIELDS)
            )

        try:
            next_kwargs = None
            USERNAME_FIELD = UserModel.USERNAME_FIELD

            # extract USERNAME_FIELD to use in query
            if USERNAME_FIELD in kwargs:
                query_kwargs = {USERNAME_FIELD: kwargs[USERNAME_FIELD]}
                next_kwargs = kwargs
                password = kwargs.get("password")

            else:  # use what is left to query
                password = kwargs.pop("password")
                query_field, query_value = kwargs.popitem()
                query_kwargs = {query_field: query_value}

            user = get_user_to_login(**query_kwargs)

            if not next_kwargs:
                next_kwargs = {
                    "password": password,
                    USERNAME_FIELD: getattr(user, USERNAME_FIELD),
                }

            return cls.parent_resolve(root, info, **next_kwargs)

        except:
            raise GraphQLError("Please enter valid credentials.")