import aws_cdk as cdk
from constructs import Construct

from stacks.api_stack import ApiStack
from stacks.database_stack import DatabaseStack
from stacks.refresh_stack import RefreshStack


class RootStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        database_stack = DatabaseStack(self, "PingDatabase")
        ApiStack(self, "PingApi")
        RefreshStack(
            self,
            "PingRefresh",
            database_table=database_stack.status_history_table,
        )
