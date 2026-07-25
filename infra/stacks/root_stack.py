import aws_cdk as cdk
from constructs import Construct

from stacks.api_stack import ApiStack
from stacks.database_stack import DatabaseStack


class RootStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, environment: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        DatabaseStack(self, "ping-database", environment)
        ApiStack(self, "ping-api", environment)
