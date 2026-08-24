from pathlib import Path

import aws_cdk as cdk
from constructs import Construct


class ApiStack(cdk.NestedStack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        api = cdk.aws_apigatewayv2.HttpApi(
            self,
            "PingApi",
            api_name="ping-api",
            cors_preflight=cdk.aws_apigatewayv2.CorsPreflightOptions(
                # TODO: temp add real
                allow_origins=["http://localhost:5173"],
                allow_methods=[
                    cdk.aws_apigatewayv2.CorsHttpMethod.GET,
                    cdk.aws_apigatewayv2.CorsHttpMethod.POST,
                    cdk.aws_apigatewayv2.CorsHttpMethod.OPTIONS,
                ],
                allow_headers=["Content-Type", "Authorization"],
            ),
        )

        # GET /hello
        hello_world_lambda_path = (
            Path(__file__).parents[2] / "backend" / "lambdas" / "hello_world"
        )
        hello_world_lambda_log_group = cdk.aws_logs.LogGroup(
            self,
            "HelloWorldLambdaLogGroup",
            retention=cdk.aws_logs.RetentionDays.TWO_WEEKS,
        )
        hello_world_lambda = cdk.aws_lambda.Function(
            self,
            "HelloWorldLambda",
            function_name="ping-hello-world",
            runtime=cdk.aws_lambda.Runtime.PYTHON_3_13,
            handler="index.main",
            code=cdk.aws_lambda.Code.from_asset(str(hello_world_lambda_path)),
            log_group=hello_world_lambda_log_group,
        )
        hello_world_lambda_integration = (
            cdk.aws_apigatewayv2_integrations.HttpLambdaIntegration(
                "HelloWorldLambdaIntegration",
                handler=hello_world_lambda,  # type:ignore
            )
        )
        api.add_routes(
            path="/hello",
            methods=[cdk.aws_apigatewayv2.HttpMethod.GET],
            integration=hello_world_lambda_integration,
        )
