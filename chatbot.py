'''
Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

    http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
'''

import sys
from dotenv import load_dotenv
import os
import irc.bot
import requests

load_dotenv()
#can access variable via os.getenv("VARIABLE")

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel
        self.botName = username


        # Validate app TOKEN
        url = 'https://id.twitch.tv/oauth2/validate'
        headers = {
        'client-id': self.client_id,
        'Authorization': 'OAuth ' + self.token
        }
        r = requests.get(url, headers=headers).json()
        #print r['client_id']
        self.currClient_ID = r['client_id']
        # Get the channel id, we will need this for API calls
        url = 'https://api.twitch.tv/helix/users?login=' + channel
        #headers = {'Client-ID': client_id}
        headers = {'client-id': self.currClient_ID, 'Authorization': 'Bearer ' + self.token}
        r = requests.get(url, headers=headers).json()
        print r['data'][0]['id']
        self.channel_id = r['data'][0]['id']

        # Get the channel id, we will need this for v5 API calls
        # url = 'https://api.twitch.tv/kraken/users?login=' + channel
        # headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        # r = requests.get(url, headers=headers).json()
        # self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print 'Connecting to ' + server + ' on port ' + str(port) + '...'
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+token)], username, username)


    def on_welcome(self, c, e):
        print 'Joining ' + self.channel

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

        #Announce bot in the channel
        c.privmsg(self.channel, self.botName + ' is in the chat!')

    def on_pubmsg(self, c, e):

        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0].split(' ')[0][1:]
            print 'Received command: ' + cmd
            self.do_command(e, cmd)
        return

    def do_command(self, e, cmd):
        c = self.connection

        # Poll the API to get current game.
        if cmd == "game":
            url = 'https://api.twitch.tv/helix/channels'
            headers = {'client-id': self.currClient_ID, 'Authorization': 'Bearer ' + self.token}
            params = {'broadcaster_id': self.channel_id}
            r = requests.get(url, headers=headers, params=params).json()['data'][0]
            c.privmsg(self.channel, r['broadcaster_name'] + ' is currently playing ' + r['game_name'])


        # Poll the API the get the current status of the stream
        elif cmd == "title":
            url = 'https://api.twitch.tv/helix/channels'
            headers = {'client-id': self.currClient_ID, 'Authorization': 'Bearer ' + self.token}
            params = {'broadcaster_id': self.channel_id}
            r = requests.get(url, headers=headers, params=params).json()['data'][0]
            c.privmsg(self.channel, r['broadcaster_name'] + ' channel title is currently ' + r['title'])

        # Provide basic information to viewers for specific commands
        elif cmd == "raffle":
            message = "This is an example bot, replace this text with your raffle text."
            c.privmsg(self.channel, message)
        elif cmd == "schedule":
            message = "This is an example bot, replace this text with your schedule text."
            c.privmsg(self.channel, message)

        # The command was not recognized
        else:
            c.privmsg(self.channel, "Did not understand command: " + cmd)

def main():

    if os.path.exists('./.env'):
        username  = os.getenv('USERNAME')
        client_id = os.getenv('CLIENT_ID')
        token     = os.getenv('TOKEN')
        channel   = os.getenv('CHANNEL')
    else:
        if len(sys.argv) != 5:
            print("Usage: twitchbot <username> <client id> <token> <channel>")
            sys.exit(1)

        username  = sys.argv[1]
        client_id = sys.argv[2]
        token     = sys.argv[3]
        channel   = sys.argv[4]

    bot = TwitchBot(username, client_id, token, channel)
    bot.start()

if __name__ == "__main__":
    main()
