import boto3
import botocore
import time

GAMING_INSTANCE_NAME = 'WHATEVER_YOU_WANT' # use whatever name you want, it doesn't matter
GAMING_INSTANCE_REGION = 'ap-east-1' # change that to your AWS region

def lambda_handler(object, context):
    instance_id = object['detail']['instance-id']

    print("SnapAndDelete! Instance ID: {}".format(instance_id))

    print("Connect to region...")
    ec2 = boto3.client('ec2')
    ec2 = boto3.client('ec2',region_name=GAMING_INSTANCE_REGION)
    res_client = boto3.resource('ec2', region_name=GAMING_INSTANCE_REGION)

    # Delete any current AMIs
    images = ec2.describe_images(Owners=['self'])['Images']
    for ami in images:
        if 'Tags' not in ami:
            continue
        for tag in ami['Tags']:
            if tag['Key'] == 'SnapAndDelete' and tag['Value'] == 'True':
                print('Retaining all snapshotIds associated to that image {}'.format(ami['ImageId']))
                snapshotIds = [device['Ebs']['SnapshotId'] for device in ami['BlockDeviceMappings'] if 'Ebs' in device]

                print('Deleting image {}'.format(ami['ImageId']))
                ec2.deregister_image(DryRun=False,ImageId=ami['ImageId'])

                print("Deleting AMI's snapshots:")
                for snapshotId in snapshotIds:
                    print('Deleting snapshot {}'.format(snapshotId))
                    ec2.delete_snapshot(SnapshotId=snapshotId)

    amis_created = []

    print("Waiting for the image to get created...")
    ami_waiter = ec2.get_waiter('image_available')

    ami = ec2.create_image(
        InstanceId=instance_id,
        Name=GAMING_INSTANCE_NAME + ' ' + time.now(),
        Description=GAMING_INSTANCE_NAME + ' Automatic AMI'
    )

    try:
        ami_waiter.wait(ImageIds=[ami['ImageId']], WaiterConfig={'Delay': 15,'MaxAttempts': 59 })
    except botocore.exceptions.WaiterError as e:
        print("Could not create AMI, aborting")
        print(e.message)
        return

    print('Created image {}'.format(ami['ImageId']))
    amis_created.append(ami['ImageId'])
    # Tag AMI
    ec2.create_tags(
        Resources=amis_created,
        Tags=[
            {'Key': 'SnapAndDelete', 'Value': 'True'},
            {'Key': 'Name', 'Value': GAMING_INSTANCE_NAME}
        ]
    )

    print("Waiting for the instance to terminate...")
    instance_waiter = ec2.get_waiter('instance_terminated')

    print('Terminating instance: {}'.format(instance_id))
    ec2.terminate_instances(InstanceIds=[instance_id])

    try:
        instance_waiter.wait(InstanceIds=[instance_id])
    except botocore.exceptions.WaiterError as e:
        print("Could not terminate instance, aborting")
        print(e.message)
        return

    # Deleting all leftover volumes
    volumes = ec2.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])['Volumes']
    if len(volumes) > 0:
        # Get all volumes for the given instance
        for volume in volumes:
            v = res_client.Volume(volume['VolumeId'])
            # TODO: this goes through but never outputs to console?
            print("Deleting EBS volume: {}, Size: {} GiB".format(v.id, v.size))
            v.delete()

    print("Done.")

    return 1