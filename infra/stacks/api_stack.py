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
                allow_headers=["Content-Type", "Authorization"],
            ),
        )

        # GET /hello
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

        # GET /sites
        check_sites_lambda_path = (
            Path(__file__).parents[2] / "backend" / "lambdas" / "check_sites"
        )
        check_sites_lambda = PythonFunction(
            self,
            "CheckSitesLambda",
            runtime=cdk.aws_lambda.Runtime.PYTHON_3_13,
            handler="main",
            entry=str(check_sites_lambda_path),
        )
        check_sites_lambda_integration = (
            cdk.aws_apigatewayv2_integrations.HttpLambdaIntegration(
                "CheckSitesLambdaIntegration", handler=check_sites_lambda
            )
        )
        api.add_routes(
            path="/sites",
            methods=[cdk.aws_apigatewayv2.HttpMethod.GET],
            integration=check_sites_lambda_integration,
        )

        api.add_stage("ApiStage", stage_name=environment.lower(), auto_deploy=True)
