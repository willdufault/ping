from pathlib import Path

import aws_cdk as cdk
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from constructs import Construct


class ApiStack(cdk.NestedStack):
    def __init__(self, scope: Construct, id: str, environment: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        api = cdk.aws_apigatewayv2.HttpApi(
            self,
            "Api",
            api_name="ping-api",
            cors_preflight=cdk.aws_apigatewayv2.CorsPreflightOptions(
                allow_origins=["http://localhost:5173"],
                allow_methods=[
                    cdk.aws_apigatewayv2.CorsHttpMethod.GET,
                    cdk.aws_apigatewayv2.CorsHttpMethod.POST,
                    cdk.aws_apigatewayv2.CorsHttpMethod.OPTIONS,
                ],
                allow_headers=["Content-Type"],
            ),
        )

        # GET /hello
        hello_world_lambda_path = (
            Path(__file__).parents[2] / "backend" / "lambdas" / "hello_world"
        )
        hello_world_lambda = cdk.aws_lambda.Function(
            self,
            "HelloWorldLambda",
            function_name="ping-hello-world",
            runtime=cdk.aws_lambda.Runtime.PYTHON_3_13,
            handler="index.main",
            code=cdk.aws_lambda.Code.from_asset(str(hello_world_lambda_path)),
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

        # GET /endpoints
        check_endpoints_lambda_path = (
            Path(__file__).parents[2] / "backend" / "lambdas" / "check_endpoints"
        )
        check_endpoints_lambda = PythonFunction(
            self,
            "CheckEndpointsLambda",
            function_name="ping-check-endpoints",
            runtime=cdk.aws_lambda.Runtime.PYTHON_3_13,
            timeout=cdk.Duration.seconds(30),
            handler="main",
            entry=str(check_endpoints_lambda_path),
        )
        check_endpoints_lambda_integration = (
            cdk.aws_apigatewayv2_integrations.HttpLambdaIntegration(
                "CheckEndpointsLambdaIntegration",
                handler=check_endpoints_lambda,  # type:ignore
            )
        )
        api.add_routes(
            path="/endpoints",
            methods=[cdk.aws_apigatewayv2.HttpMethod.GET],
            integration=check_endpoints_lambda_integration,
        )

        api.add_stage("ApiStage", stage_name=environment.lower(), auto_deploy=True)
