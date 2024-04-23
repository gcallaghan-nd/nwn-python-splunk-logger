# Python Splunk Logger

This custom logger can be used to implement Splunk logging. Any logs sent to this logger will also be logged using the standard logging system.

## Install
This package is hosted on the NW Natural ADO project for the Enterprise Generative AI Platform.
The feed is located here:
    https://dev.azure.com/nwnatural/Enterprise%20Generative%20AI%20Platform/_artifacts/feed/Shared@1c5e229f-a4e0-4186-912e-ac440802cc99

Add a line at the top of your requirements.txt file to point to the feed:
    --extra-index-url https://pkgs.dev.azure.com/GeoffCallaghanND/_packaging/nwn_feed/pypi/simple/

The first time you run a pip install you'll be asked for a username and password. Username is your NWN email, and the password is a Personal Access Token that you'll have to generate in ADO. Once you have entered them, you'll be asked if you want to add them to the keyring. Say Yes; after this, future installations will not require the login.




