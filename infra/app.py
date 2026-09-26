import aws_cdk as cdk

from stacks.root_stack import RootStack

TAGS = {"Project": "ping"}
REGIONS = ["us-east-1", "us-east-2"]

app = cdk.App()
RootStack(app, "ping-root", tags=TAGS, regions=REGIONS)
app.synth()
