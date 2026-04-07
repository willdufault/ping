import aws_cdk as cdk
from stacks.database_stack import DatabaseStack
from stacks.api_stack import ApiStack

from constructs import Construct


class RootStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, environment: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        DatabaseStack(self, "ping-database")
        ApiStack(self, "ping-api", environment)
