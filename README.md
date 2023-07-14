# cibot
CI Bot was built in python using discord.py. It provides quality of life features to identify leaks.

Burn Relays
------
As of 2023, Discord fetches images to embed from sites (CDN) on a guild by guild basis.
If I host smug.jpeg on my webserver then post the link in a channel being relayed instead of fetching it once, discord will attempt to fetch it twice because it is being relayed.
Many people forgot about this as most relays in the modern day attempt to resolve this issue by adding a zero-width character in links to prevent the embed. However, they do not check for the image links inside of embeds.
Therefore, you can get around this "relay protection" through this.

Most relays will deativate when either the discord client has user roles or channel permissions. You can occasionally play with some channel settings so that they are forced to toggle this off.
In combination with this you can occasionally cycle through a list of all users with a set role such as Member and send a ping with the name/discord id of the user locked to that channel.
If you have access a relay it will reveal the identity of the user relaying. Additionally, a random number from 1000-9999 is added so if someone tries to make up a user you can confirm from a log channel that information is correct.

Simple Commands
-----
Split Roles command divides groups in half. It allows me to isolate specific groups without having to manually add users to a group.
Copy Permisisons command exists to add copy permissions from one channel to another. It is good for temporary making a makeshift channel then tampering with another to catch a relay.
Search command exists to search for users with set roles. By default CI Bot will bolden users with "Corp Leadership" role and give them the (CAP/SCAP) tag based on if they have the CAPITAL or SUPERCAPITAL groups.
Lookup command allows users to search general information about a character. Including the blacklist status and recruitability recommendation risk metric (WIP).

General Notifcations:
* When users join with a discord account younger than 90 days.
* When people leave with a specific group. eg. Capital groups.
* Notificatins when users are flagged with Mumble hashes of known hostiles. (Porting over to new version).

Installation:
Installing and hosting CI Bot yourself is very straight forward.
1) Install the latest version of Python 3 (For Windows: ensure you have the python path set properly).
2) Open Command Prompt / Terminal write "cd location_of_cibot"
3) Create a Virtual Environment by writing "python3 -m 3 venv cibot"
4) Write "cd cibot" and add "cibot.py" & "requirements.txt" into the cibot folder.
5) Linux users write "source bin/activate" Windows users write .\Scripts\activate.
6) After that write pip install requirements.txt
7) At the bottom of cibot.py change the BOT_TOKEN to your bot token (https://discord.com/developers/applications), change the GUILD_ID to your guild ID, and SYSTEM_MESSAGE_CHANNEL to your system message channel id.
8) CI Bot should then run perfectly. Congrats! Good luck hunting. 
