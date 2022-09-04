# AWS-SnapAndDelete-Lambda
lambda scripts for start/stop instances for cloud gaming in a cost-effective way

# `snap-and-delete-on-stop.py`
- create a lambda function and copy/paste the code in it.
- using EventBridge, create a new rule with the following event pattern:

```
{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance State-change Notification"],
  "detail": {
    "state": ["stopped"]
  }
}```

- and use the lambda function you created as a target.
- that way, each time you stop an instance it will:
  - delete old AMIs and their associated snapshots
  - create a new AMI of the instance that got stopped
  - terminate the instance
  - delete all remaining volumes (**be careful, it will delete ALL volumes!!!**)