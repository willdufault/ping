import aws_cdk as cdk
from pathlib import Path

from constructs import Construct


class ApiStack(cdk.NestedStack):
    def __init__(self, scope: Construct, id: str, environment: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        api = cdk.aws_apigatewayv2.HttpApi(self, "Api", api_name="ping-api")

        hello_world_lambda_path = (
            Path(__file__).parents[2] / "backend" / "lambdas" / "hello_world"
        )
        hello_world_lambda = cdk.aws_lambda.Function(
            self,
            "HelloWorldLambda",
            runtime=cdk.aws_lambda.Runtime.PYTHON_3_13,
            handler="index.main",
            code=cdk.aws_lambda.Code.from_asset(str(hello_world_lambda_path)),
        )

        hello_world_lambda_integration = (
            cdk.aws_apigatewayv2_integrations.HttpLambdaIntegration(
                "HelloWorldLambdaIntegration", handler=hello_world_lambda
            )
        )

        api.add_routes(
            path="/hello",
            methods=[cdk.aws_apigatewayv2.HttpMethod.GET],
            integration=hello_world_lambda_integration,
        )

        api.add_stage("ApiStage", stage_name=environment.lower(), auto_deploy=True)
