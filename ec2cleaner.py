# This script basically checks the live ec2 instances based on supplied tag
# if the tag is not found it would terminate the instance
import re
from urllib import response
import boto3
import os
# Access Secret Key variables
ACCESS_KEY_AWS="xxx"
SECRET_KEY_AWS="xxxx"
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

def region_list():
    # list all the regions that AWS has, it is dynamic and would list available regions at that point it time, if any new regions are introduced this would cover that as well
    region_list=[]
    ec2_client = boto3.client('ec2', aws_access_key_id=ACCESS_KEY_AWS,aws_secret_access_key=SECRET_KEY_AWS)
    response_regions = ec2_client.describe_regions()
    for list_name in range(len(response_regions["Regions"])):
        region_list.append(response_regions["Regions"][list_name]["RegionName"])
    return region_list

def ec2_list(region_list):
    # This code will collect list of all ec2 instance mapped with regions which does not have auto-delete tag added
    # auto-delete tag in place indicates that this should not be deleted, if tag is not present it would collect ec2 instanceid-region and add it in terminate queue
    terminate_instance={}
    terminate_instance["instanceid"]=[]
    try:
        for list_reg in range(len(region_list)):
            regioncount=1
            ec2_client = boto3.client('ec2', aws_access_key_id=ACCESS_KEY_AWS,aws_secret_access_key=SECRET_KEY_AWS,region_name=str(region_list[list_reg]))
            response_ec2_list = ec2_client.describe_instances()
            for instance_id_list in range (len(response_ec2_list["Reservations"])):
                not_add=0
                try:
                    if response_ec2_list["Reservations"][instance_id_list]["Instances"][0]["Tags"] :
                        for tag_len in range (len(response_ec2_list["Reservations"][instance_id_list]["Instances"][0]["Tags"])):
                            if(response_ec2_list["Reservations"][instance_id_list]["Instances"][0]["Tags"][tag_len]["Key"].lower()) == "auto-delete":
                                not_add=1
                                break
                            else:
                                continue
                        if (not_add==0):
                            terminate_instance["instanceid"].append(response_ec2_list["Reservations"][instance_id_list]["Instances"][0]["InstanceId"]+"::"+str(region_list[list_reg]))
                    else:
                        terminate_instance["instanceid"].append(response_ec2_list["Reservations"][instance_id_list]["Instances"][0]["InstanceId"])
                    regioncount+=1
                except Exception as e:
                    terminate_instance["instanceid"].append(response_ec2_list["Reservations"][instance_id_list]["Instances"][0]["InstanceId"])
                    print(e)
                    regioncount+=1
    except Exception as e:
        print(e)
    return terminate_instance

def terminate_ec2_instances(terminate_list):
    # This code would terminate based on the list obtained from ec2_list function 
    for term_list in range(len(terminate_list["instanceid"])):
        inst_reg_seperator=terminate_list["instanceid"][term_list]
        inst_reg_seperated=inst_reg_seperator.split("::")
        print(inst_reg_seperated)
        ec2_client = boto3.client('ec2', aws_access_key_id=ACCESS_KEY_AWS,aws_secret_access_key=SECRET_KEY_AWS,region_name=str(inst_reg_seperated[1]))
        try:    
            response_term = ec2_client.terminate_instances(
                InstanceIds=[inst_reg_seperated[0]],
                # Keep DryRun variable True and validate the list of instances that would get terminated
                # If any important instance is getting terminated then add the tag auto-delete with any value and the instance would not appear in re run
                # Once confirmed change DryRun to False and add script as daily schedule 
                DryRun=True  
                )
            print(response_term)
        except Exception as e:
            print(e)

region_list=region_list()
ec2_terminate_list=ec2_list(region_list)
print(ec2_terminate_list)
terminate_ec2_instances(ec2_terminate_list)