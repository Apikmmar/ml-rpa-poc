from aws_cdk import (
    CfnOutput,
    aws_apigateway as apigw,
)
from constructs import Construct
from .config import PREFIX

class ApiGatewayStack(Construct):

    def __init__(self, scope: Construct, construct_id: str, lambda_stack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        api = apigw.RestApi(
            self, "PresignApi",
            description="API for RPA proof-of-concept",
            rest_api_name=f"{PREFIX}PresignAPI",
        )
        
        upload_url = api.root.add_resource(
            "upload-url",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=["GET", "OPTIONS"],
                allow_headers=apigw.Cors.DEFAULT_HEADERS
            )
        )
        upload_url.add_method(
            "GET", apigw.LambdaIntegration(lambda_stack.presign_lambda)
        )
        CfnOutput(self, "PresignApiUrl", value=f"{api.url}upload-url")
