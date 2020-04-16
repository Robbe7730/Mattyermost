import mattermost
import configparser
from pprint import pprint
import sys

def eprint(message):
   print(message, file=sys.stderr)

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

    # Create a message
    mm.create_post(config["mattermost"]["channel_id"], "TEST")
    

if __name__ == "__main__":
    main()
