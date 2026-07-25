import aws_cdk as cdk
from aws_cdk.aws_dynamodb import AttributeType
from constructs import Construct


class DatabaseStack(cdk.NestedStack):
    def __init__(self, scope: Construct, id: str, environment: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        responses_table = cdk.aws_dynamodb.TableV2(
            self,
            "PingResponsesTable",
            table_name=f"ping-responses-{environment.lower()}",
            partition_key=cdk.aws_dynamodb.Attribute(
                name="PK", type=AttributeType.STRING
            ),
            sort_key=cdk.aws_dynamodb.Attribute(name="SK", type=AttributeType.STRING),
        )
