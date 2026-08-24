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
        **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        check_services_lambda_path = (
            Path(__file__).parents[2] / "backend" / "lambdas" / "check_services"
        )
        check_services_lambda_log_group = cdk.aws_logs.LogGroup(
            self,
            "CheckServicesLambdaLogGroup",
            retention=cdk.aws_logs.RetentionDays.TWO_WEEKS,
        )

        check_services_lambda_role = cdk.aws_iam.Role(
            self,
            "CheckServicesLambdaRole",
            role_name="ping_check_services_lambda_role",
            assumed_by=cdk.aws_iam.ServicePrincipal("lambda.amazonaws.com"),
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
                                "s3:ListBuckets",
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

        check_services_lambda = PythonFunction(
            self,
            "CheckServicesLambda",
            function_name="ping_check_services_lambda",
            runtime=cdk.aws_lambda.Runtime.PYTHON_3_13,
            timeout=cdk.Duration.seconds(30),
            handler="main",
            entry=str(check_services_lambda_path),
            log_group=check_services_lambda_log_group,
            role=check_services_lambda_role,
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
                            resources=[check_services_lambda.function_arn],
                        )
                    ]
                )
            },
        )

        cdk.aws_scheduler.CfnSchedule(
            self,
            "CheckServicesSchedule",
            name="ping_refresh_schedule",
            schedule_expression="cron(0/30 * * * ? *)",
            schedule_expression_timezone="America/New_York",
            flexible_time_window=cdk.aws_scheduler.CfnSchedule.FlexibleTimeWindowProperty(
                mode="OFF",
            ),
            target=cdk.aws_scheduler.CfnSchedule.TargetProperty(
                arn=check_services_lambda.function_arn,
                role_arn=schedule_role.role_arn,
            ),
        )
