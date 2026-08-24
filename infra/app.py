import aws_cdk as cdk

from stacks.root_stack import RootStack

TAGS = {"Project": "ping"}

app = cdk.App()
RootStack(app, f"ping-root", tags=TAGS)
app.synth()
