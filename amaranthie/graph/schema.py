import strawberry
import typing

@strawberry.type
class Query:

    @strawberry.field
    def hello() -> str:
        return "hello, world"

schema = strawberry.Schema(query=Query)
