# AWS-SnapAndDelete-Lambda
lambda scripts for start/stop instances for cloud gaming in a cost-effective way

# BEWARE!
- those lambda scripts are provided AS-IS, if you are not experienced with AWS **DO NOT USE!**
  - AWS bills can go crazy high FAST if you don't know what you're doing.
  - i will provide no support for these, they are just scripts i've built for myself

# `snap-and-delete-on-stop.py`
- create a lambda function and copy/paste the code in it.
- make sure you set the timeout to some higher value ie. 15mins
- make sure you give the lambda permission:
  - click on `Permissions` from the top, and click on the role that AWS automatically created for your function.
  - click `Attach Policies`, search for EC2 and choose the `AmazonEC2FullAccess` policy. click `Attach Policy`
- using `EventBridge`, create a new rule with the following event pattern:

```
{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance State-change Notification"],
  "detail": {
    "state": ["stopped"]
  }
}
```

- and use the lambda function you created as a target.
- that way, each time you stop an instance it will:
  - delete old AMIs and their associated snapshots
  - create a new AMI of the instance that got stopped
  - terminate the instance
  - delete all remaining volumes (**be careful, it will delete ALL volumes!!!**)

# `spawn-instance-from-image.py`
- a script you can call using a bash or powershell script to redeploy the imaged instance
- follow the same lambda instructions as above (permissions, timeout, etc.)
- create a function URL (in the lambda configuration) that you can call via `curl`
- call that url whenever you need to spawn an instance of the last created AMI