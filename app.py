import os
import aws_cdk as cdk
from ml_rpa_poc.ml_rpa_poc_stack import MlRpaPocStack

app = cdk.App()
MlRpaPocStack(app, "MlRpaPocStack",
    env=cdk.Environment(region='ap-southeast-1')
)

app.synth()