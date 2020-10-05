import graphene
import users.schema
import movies.schema


class Query(users.schema.Query, movies.schema.Query, graphene.ObjectType):
    pass


class Mutation(users.schema.Mutation, movies.schema.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)