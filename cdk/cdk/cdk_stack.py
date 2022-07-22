from aws_cdk import (
    aws_autoscaling as autoscaling,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    App, CfnOutput, Stack
)

from constructs import Construct

class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, "MyVpc", max_azs=2)     # default is all AZs in region

        cluster = ecs.Cluster(self, "circleci-multiarch-demo", vpc=vpc)

        fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
            self, "FargateService",
            cluster=cluster,
            task_image_options=ecs_patterns.NetworkLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample")
            )
        )

        fargate_service.service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection = ec2.Port.tcp(8080),
            description="Allow http inbound from VPC"
        )

        CfnOutput(
            self, "LoadBalancerDNS",
            value=fargate_service.load_balancer.load_balancer_dns_name
        )

app = App()
app.synth()