import aws_cdk as cdk

from stacks.root_stack import RootStack

TAGS = {
    "Project": "ping",
    "Environment": "Dev",
}

app = cdk.App()
RootStack(app, "ping-root", TAGS["Environment"], tags=TAGS)
app.synth()
