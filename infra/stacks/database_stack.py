import aws_cdk as cdk
from aws_cdk.aws_dynamodb import AttributeType
from constructs import Construct


class DatabaseStack(cdk.NestedStack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        site_results_table = cdk.aws_dynamodb.TableV2(
            self,
            "SiteResultsTable",
            table_name="PingSiteResults",
            partition_key=cdk.aws_dynamodb.Attribute(
                name="PK", type=AttributeType.STRING
            ),
        )
