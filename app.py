import mattermost
import mattermost.ws
import configparser
import pty
from pprint import pprint
import sys
import os
import json

def eprint(message):
   print(message, file=sys.stderr)

def read_from_pty(fd, mm, config):
    data = os.read(fd, 100000)
    mm.create_post(config["mattermost"]["channel_id"], f"`{data.decode('utf-8')}`")
    return data

def handle_ws(mm_ws, data, pty):
    if data["event"] == "posted":
        message = json.loads(data["data"]["post"])["message"]
        if message[0] != '`':
            os.write(6, bytes(message + "\n", "utf-8"))
    pass

def main():
    # Read in the config
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Setup Mattermost connection
    mm = mattermost.MMApi(config["mattermost"]["url"])
    mm.login(bearer=config["mattermost"]["token"])
    user = mm.get_user()

    # Check for team id
    if "team_id" not in config["mattermost"]:
        available_teams = mm.get_teams()
        eprint("No team_id set in config.ini, please select one:")
        for team in available_teams:
            eprint(f" - {team['display_name']}: {team['id']}")
        return

    # Check for channel id
    if "channel_id" not in config["mattermost"]:
        available_channels = mm.get_channels_for_user(user["id"], config["mattermost"]["team_id"])
        eprint("No channel_id set in config.ini, please select one:")
        for channel in available_channels:
            eprint(f" - {channel['display_name']}: {channel['id']}")
        return

    mm_ws = mattermost.ws.MMws(lambda mm_ws, data: handle_ws(mm_ws, data, pty), mm, config["mattermost"]["ws_url"])

    # Spawn a new bash shell, sending all output to Mattermost
    pty.spawn("/bin/bash", lambda fd: read_from_pty(fd, mm, config))
    pty.fork()

if __name__ == "__main__":
    main()
