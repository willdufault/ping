from pathlib import Path

import aws_cdk as cdk
from constructs import Construct


class ApiStack(cdk.NestedStack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        database_table: cdk.aws_dynamodb.TableV2,
        regions: list[str],
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)
        api = cdk.aws_apigatewayv2.HttpApi(
            self,
            "PingApi",
            api_name="ping_api",
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

        get_service_statuses_lambda_path = (
            Path(__file__).parents[2] / "backend" / "lambdas" / "get_service_statuses"
        )
        get_service_statuses_lambda_log_group = cdk.aws_logs.LogGroup(
            self,
            "GetServiceStatusesLambdaLogGroup",
            retention=cdk.aws_logs.RetentionDays.TWO_WEEKS,
        )
        get_service_statuses_lambda_role = cdk.aws_iam.Role(
            self,
            "GetServiceStatusesLambdaRole",
            assumed_by=cdk.aws_iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                cdk.aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
            inline_policies={
                "StatusHistoryRead": cdk.aws_iam.PolicyDocument(
                    statements=[
                        cdk.aws_iam.PolicyStatement(
                            actions=["dynamodb:Query"],
                            resources=[database_table.table_arn],
                        )
                    ]
                )
            },
        )
        get_service_statuses_lambda = cdk.aws_lambda.Function(
            self,
            "GetServiceStatusesLambda",
            function_name="ping_get_service_statuses_lambda",
            runtime=cdk.aws_lambda.Runtime.PYTHON_3_13,
            handler="index.main",
            code=cdk.aws_lambda.Code.from_asset(str(get_service_statuses_lambda_path)),
            timeout=cdk.Duration.seconds(30),
            log_group=get_service_statuses_lambda_log_group,
            role=get_service_statuses_lambda_role,
            environment={
                "table_name": database_table.table_name,
                "table_region": cdk.Aws.REGION,
                "regions": ",".join(regions),
            },
        )
        get_service_statuses_lambda_integration = (
            cdk.aws_apigatewayv2_integrations.HttpLambdaIntegration(
                "GetServiceStatusesLambdaIntegration",
                handler=get_service_statuses_lambda,  # type:ignore
            )
        )
        api.add_routes(
            path="/status",
            methods=[cdk.aws_apigatewayv2.HttpMethod.GET],
            integration=get_service_statuses_lambda_integration,
        )
