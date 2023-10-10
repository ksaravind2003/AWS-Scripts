
# This script finds all unused security groups in a single AWS Region

import boto3

if __name__ == "__main__":
    ec2 = boto3.client("ec2")
    
    regions = ec2.describe_regions().get('Regions',[] )

    # Iterate over regions
    for region in regions:

        reg=region['RegionName']
        
        used_SG = set()
        total_SG = set()
        unused_SG = set()
        
        client = boto3.client('ec2', region_name=reg)
        elb = boto3.client("elb", region_name=reg)
        elbv2 = boto3.client("elbv2", region_name=reg)
        rds = boto3.client("rds", region_name=reg)
        
        # Find security groups attached to ENIs
        response = client.describe_network_interfaces()
        for eni in response["NetworkInterfaces"]:
            for sg in eni["Groups"]:
                used_SG.add(sg["GroupId"])

        # Find EC2 instances security group in use.
        response = client.describe_instances()
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                for sg in instance["SecurityGroups"]:
                    used_SG.add(sg["GroupId"])

        # Find Classic load balancer security group in use
        response = elb.describe_load_balancers()
        for lb in response["LoadBalancerDescriptions"]:
            for sg in lb["SecurityGroups"]:
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

        response = client.describe_security_groups()
        total_SG = [sg["GroupId"] for sg in response["SecurityGroups"]]
        unused_SG = set(total_SG) - used_SG
        
        print ("* Checking region  --   %s " % region['RegionName'])
        print()

        print(f"Total Security Groups: {len(total_SG)}")
        print(f"{list(total_SG)}")
        print()

        print(f"Used Security Groups: {len(used_SG)}")
        print(f"{list(used_SG)}")
        print()

        print(f"Unused Security Groups: {len(unused_SG)} compiled in the following list:")
        print(f"{list(unused_SG)}")
        print()
