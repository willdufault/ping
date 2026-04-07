from stacks.root_stack import RootStack
import aws_cdk as cdk

TAGS = {
    "Project": "ping",
    "Environment": "Dev",
    "CreatedBy": "Will",
}

app = cdk.App()
RootStack(app, "ping-root", TAGS["Environment"], tags=TAGS)
app.synth()
