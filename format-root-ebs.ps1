# get rid of the pesky "you need to format disk" prompt
Stop-Service -Name ShellHWDetection

echo "Attempting to format root EBS volume..."
$newDisks = Get-Disk | Where-Object PartitionStyle –Eq 'RAW'
$usedLetters = (Get-Volume).DriveLetter

foreach ($disk in $newDisks){
    echo "Set disk to online"
    try {
        Set-Disk -Number $disk.Number -IsOffline $False
    }
    catch {
        echo "Could not get disk online"
    }
    echo "Create partition"
    try {
        Initialize-Disk -Number $disk.Number -PartitionStyle "MBR"
    }
    catch {
        echo "Initialization failed"
    }
    try {
        $partition = New-Partition -DiskNumber $disk.Number -UseMaximumSize
        # CHANGE LETTER BASED ON YOUR NEEDS
        echo "assign letter G to drive"
        $partition | Set-Partition -NewDriveLetter G
    }
    catch {
        echo "Partition failed"
    }

    echo "Finally format the drive with the letter"
    try {
        Format-Volume -DriveLetter G -FileSystem NTFS -Confirm:$FALSE
    }
    catch {
        echo "Format failed"
    }
}
