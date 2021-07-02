now=$(date)
echo "Starting at "$now
result=$(python3 regular_slack_notification.py)
if [ -z "$var" ]
then
    echo "No user with old access key"
else
    users=($(echo $result | tr " " "\n"))
    for i in "${users[@]}"
    do
        python3 warning_email.py $i
        echo "Warning Email Sent for user $i"
        echo "python3 deactivate_key.py $i > deactivation_log.txt" | at now + 3 days
        echo "python3 ./delete_key.py $i > deletion_log.txt" | at now + 15 days
    done
fi
