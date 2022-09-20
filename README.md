# BEWARE!
- those scripts are provided AS-IS, if you are not well experienced with AWS **PLEASE DO NOT USE!**
  - AWS bills can go crazy high FAST if you don't know what you're doing.
  - if something wrong happens, i am **not** responsible and **i will provide no support**.

# random bits of advice
- use `gp3` instead of `gp2` for volume types, it is most cost efficient / cheaper by about 30%
- as the following script implies, convert unused volumes to snapshots, and if you really don't use them often don't hesitate to archive the snapshots.
  - snapshots are about half cheaper and archives are maybe 10 times even cheaper.
- as this script uses, `g4dn` are IMO the best instance type to use at the moment and it is good enough to run most AAA games.
- for huge games like Red Dead Redemption, a costly yet efficient way to speed up loading times and in-game texture streaming is to increase the volume `Throughput`.
  - **BEWARE!** It cost a EXPONENTIALLY more than the defaults (default is 125MB/s) 
- you can use the same `spawn-instance-from-image.py` script for spot instances. Make sure you are allowed by AWS to use them first.

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

# `format-root-ebs.ps1`
- this script is meant to be ran ON the instance.
- CHANGE THE DRIVE LETTER based on your needs (hardcoded to `G`)
- script that can be executed on startup to format the ephemeral EBS root volume to NTFS.
- to execute on startup you can add a `cmd` script to the startup directory ie.
  - in `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp`
  - create a `startFormatRootEBS.cmd` file and do something like:
```
PowerShell -Command "Set-ExecutionPolicy Unrestricted" >> "%TEMP%\StartupLog.txt" 2>&1
PowerShell %USERPROFILE%\Desktop\format-root-ebs.ps1 >> "%TEMP%\StartupLog.txt" 2>&1
```
