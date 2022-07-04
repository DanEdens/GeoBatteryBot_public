mosquitto_sub -h %awsip% -p %awsport% -v -t "battery_tracker/#" | xargs -o -r -I {} python __main__.py {}
