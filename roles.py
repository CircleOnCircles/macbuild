def macos(elite, computer_sleep_time, display_sleep_time, timezone):
    computer_sleep = elite.run(command='systemsetup -getcomputersleep', sudo=True, changed=False)
    if (
        f'Computer Sleep: {computer_sleep_time}' !=
        computer_sleep.stdout.rstrip().replace('after ', '').replace('minutes', '')
    ):
        elite.run(
            command=f'systemsetup -setcomputersleep {computer_sleep_time}', sudo=True
        )

    display_sleep = elite.run(command='systemsetup -getdisplaysleep', sudo=True, changed=False)
    if (
        f'Display Sleep: {display_sleep_time}' !=
        display_sleep.stdout.rstrip().replace('after ', '').replace('minutes', '')
    ):
        elite.run(
            command=f'systemsetup -setdisplaysleep {display_sleep_time}', sudo=True
        )

    current_timezone = elite.run(command='systemsetup -gettimezone', sudo=True, changed=False)
    if f'Time Zone: {timezone}' != current_timezone.stdout.rstrip():
        elite.run(command=f'systemsetup -settimezone {timezone}', sudo=True)
