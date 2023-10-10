# This script finds all unused security groups in a single AWS Region
# Configure the region under Config -- region_name

import boto3
from botocore.config import Config

if __name__ == "__main__":
    my_config = Config(
        region_name = 'ap-southeast-1',
        signature_version = 'v4',
        retries = {
            'max_attempts': 10,
            'mode': 'standard'
        }
    )

    ec2 = boto3.client("ec2", config=my_config)
    elb = boto3.client("elb", config=my_config)
    elbv2 = boto3.client("elbv2", config=my_config)
    rds = boto3.client("rds", config=my_config)

    used_SG = set()

    # Find security groups attached to ENIs
    response = ec2.describe_network_interfaces()
    for eni in response["NetworkInterfaces"]:
        for sg in eni["Groups"]:
            if sg['GroupName'].lower() != 'default':
                used_SG.add(sg["GroupId"])

    # Find EC2 instances security group in use.
    response = ec2.describe_instances()
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            for sg in instance["SecurityGroups"]:
                if sg['GroupName'].lower() != 'default':
                    used_SG.add(sg["GroupId"])

    # Find Classic load balancer security group in use
    response = elb.describe_load_balancers()
    for lb in response["LoadBalancerDescriptions"]:
        for sg in lb["SecurityGroups"]:
            if sg['GroupName'].lower() != 'default':
                used_SG.add(sg)

    # Find Application load balancer security group in use
    response = elbv2.describe_load_balancers()
    for lb in response["LoadBalancers"]:
        for sg in lb["SecurityGroups"]:    
            used_SG.add(sg)

    # Find RDS db security group in use
    response = rds.describe_db_instances()
    for instance in response["DBInstances"]:
        for sg in instance["VpcSecurityGroups"]:
            used_SG.add(sg["VpcSecurityGroupId"])

    response = ec2.describe_security_groups()
    total_SG = [sg["GroupId"] for sg in response["SecurityGroups"] if sg['GroupName'].lower() != 'default']
    unused_SG = set(total_SG) - used_SG

    print(f"Total Security Groups: {len(total_SG)}")
    for sg in response["SecurityGroups"]:
        print(f"{sg['GroupId']} - {sg['GroupName']}")
    
    print()
    print(f"Used Security Groups: {len(used_SG)}")
    print(f"{list(used_SG)}")
    print()

    print(f"Unused Security Groups: {len(unused_SG)} compiled in the following list:")
    print(f"{list(unused_SG)}")
    print()
