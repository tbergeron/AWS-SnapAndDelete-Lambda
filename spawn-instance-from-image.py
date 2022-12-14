import boto3
import botocore

GAMING_INSTANCE_NAME = 'WHATEVER_YOU_WANT' # use whatever name you want, it doesn't matter
GAMING_INSTANCE_REGION = 'ap-east-1' # change that to your AWS region
INSTANCE_TYPE = 'g4dn.xlarge'
KEYPAIR_NAME = 'keypair-name' # the keypair you'd select when creating a new ec2 instance

def image_sort(elem):
    return elem.get('CreationDate')

def lambda_handler(object, context):
    print("SpawnInstanceFromImage!")

    print("Connect to region...")
    ec2 = boto3.client('ec2')
    ec2 = boto3.client('ec2',region_name=GAMING_INSTANCE_REGION)
    res_client = boto3.resource('ec2', region_name=GAMING_INSTANCE_REGION)

    print("Fetching images...")
    images = ec2.describe_images(Owners=['self'])['Images']
    images.sort(key=image_sort, reverse=True)

    print("Retaining last created image ID and name")
    image_id = images[0]['ImageId']
    image_name = images[0]['Name']

    print("Spawning new instance {}, based on image ID: {}".format(image_name, image_id))
    res_client.create_instances(
        ImageId=image_id,
        MinCount=1,
        MaxCount=1,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEYPAIR_NAME,
	# To use spot instances instead, uncomment the below and tweak to your likings:
    #     InstanceMarketOptions={
    #         'MarketType': 'spot',
    #         'SpotOptions': {
    #             'MaxPrice': '0.5', # Check "Instances -> Spot Requests -> Pricing history"
    #             'SpotInstanceType': 'persistent',
    #             'InstanceInterruptionBehavior': 'stop'
    #         }
    #     },
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': image_name
                    },
                ]
            },
        ]
    )

    print("Done.")

    return 1