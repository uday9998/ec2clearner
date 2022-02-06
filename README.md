# ec2clearner
This contains the code to cleanup ec2 environment in AWS
This scripts checks for the ec2 instances that does not contain tag auto-delete and create the list of those ec2 instances
Once the list is available it will go ahead and terminate the instance based on Dry run Flag, if it is set to false it would just DryRun the script, if it is set to True it would go ahead and termiate those instances
