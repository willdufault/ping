from pathlib import Path

import aws_cdk as cdk
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from constructs import Construct


class RefreshStack(cdk.NestedStack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        database_table: cdk.aws_dynamodb.TableV2,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        collect_service_statuses_lambda_path = (
            Path(__file__).parents[2]
            / "backend"
            / "lambdas"
            / "collect_service_statuses"
        )
        collect_service_statuses_lambda_log_group = cdk.aws_logs.LogGroup(
            self,
            "CollectServiceStatusesLambdaLogGroup",
            retention=cdk.aws_logs.RetentionDays.TWO_WEEKS,
        )

        collect_service_statuses_lambda_role = cdk.aws_iam.Role(
            self,
            "CollectServiceStatusesLambdaRole",
            role_name="ping_collect_service_statuses_lambda_role",
            assumed_by=cdk.aws_iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                cdk.aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
            inline_policies={
                "RoleAccess": cdk.aws_iam.PolicyDocument(
                    statements=[
                        cdk.aws_iam.PolicyStatement(
                            actions=["dynamodb:GetItem", "dynamodb:PutItem"],
                            resources=[database_table.table_arn],
                        ),
                        cdk.aws_iam.PolicyStatement(
                            actions=[
                                "ec2:DescribeInstances",
                                "s3:ListAllMyBuckets",
                                "lambda:ListFunctions",
                                "dynamodb:ListTables",
                                "cloudfront:ListDistributions",
                            ],
                            resources=["*"],
                        ),
                    ]
                )
            },
        )

        collect_service_statuses_lambda = PythonFunction(
            self,
            "CollectServiceStatusesLambda",
            function_name="ping_collect_service_statuses_lambda",
            runtime=cdk.aws_lambda.Runtime.PYTHON_3_13,
            timeout=cdk.Duration.seconds(30),
            handler="main",
            entry=str(collect_service_statuses_lambda_path),
            log_group=collect_service_statuses_lambda_log_group,
            role=collect_service_statuses_lambda_role,
            environment={
                "table_name": database_table.table_name,
                "table_region": cdk.Aws.REGION,
            },
        )

        schedule_role = cdk.aws_iam.Role(
            self,
            "ScheduleRole",
            role_name="ping_refresh_schedule_role",
            assumed_by=cdk.aws_iam.ServicePrincipal(  # type:ignore
                "scheduler.amazonaws.com"
            ),
            inline_policies={
                "InvokeLambda": cdk.aws_iam.PolicyDocument(
                    statements=[
                        cdk.aws_iam.PolicyStatement(
                            actions=["lambda:InvokeFunction"],
                            resources=[collect_service_statuses_lambda.function_arn],
                        )
                    ]
                )
            },
        )

        cdk.aws_scheduler.CfnSchedule(
            self,
            "CollectServiceStatusesSchedule",
            name="ping_refresh_schedule",
            schedule_expression="cron(0/30 * * * ? *)",
            schedule_expression_timezone="America/New_York",
            flexible_time_window=cdk.aws_scheduler.CfnSchedule.FlexibleTimeWindowProperty(
                mode="OFF",
            ),
            target=cdk.aws_scheduler.CfnSchedule.TargetProperty(
                arn=collect_service_statuses_lambda.function_arn,
                role_arn=schedule_role.role_arn,
            ),
        )
