from stacks.root_stack import RootStack
import aws_cdk as cdk

TAGS = {
    "Project": "ping",
    "Environment": "Dev",
    "CreatedBy": "Will",
}

# TODO: add names to all stack resources (if possible. ex: see lambda names in console)
app = cdk.App()
RootStack(app, "ping-root", TAGS["Environment"], tags=TAGS)
app.synth()
