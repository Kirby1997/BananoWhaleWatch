import twitter
import socket
import re
import time
import json

with open("config.json") as config:
    config = json.load(config)
    ckey = config["consumer_key"]
    csec = config["consumer_secret"]
    akey = config["access_token_key"]
    asec = config["access_token_secret"]
    listenIP = config["listenIP"]
    listenPort = config["listenPort"]
    twitacc= config["twitacc"]


api = twitter.Api(consumer_key=ckey,
                      consumer_secret=csec,
                      access_token_key=akey,
                      access_token_secret=asec)

print(api.VerifyCredentials())


# Function written by Bbedward as part of MonkeyTalks
def get_banano_address(input_text: str) -> str:
    """Extract a banano address from a string using regex"""
    address_regex = '(?:ban)(?:_)(?:1|3)(?:[13456789abcdefghijkmnopqrstuwxyz]{59})'
    matches = re.findall(address_regex, input_text)
    if len(matches) == 1:
        return matches[0]
    return None


def createServer():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lastsender = ""
    lastamount = ""
    lastrecipient = ""
    throttle = False
    lastTweet = ""
    try:
        serversocket.bind((listenIP, listenPort))
        serversocket.listen(5)
        while(1):
            tweets = api.GetUserTimeline(user_id=twitacc, count=1)
            lastTweet = tweets[0].text
            (clientsocket, address) = serversocket.accept()
            received = clientsocket.recv(5000).decode()
            pieces = received.split("\n")
            if len(pieces) == 13:
                useful = [pieces[6], pieces[7], pieces[9]]
                parts = []
                if pieces[10].strip("} ") == "\"is_send\": \"true\"":
                    for item in useful:
                        item = item.split(":")
                        item = item[1].strip()
                        item = item.strip(",")
                        item = item.strip('\"')
                        parts.append(item)

                split = pieces[8].split("\\n")
                sender = parts[0]
                block = parts[1]
                recipient = get_banano_address(split[7])
                amount = int(parts[2]) / 10 ** 29
                if amount >= 50_000 and recipient != lastsender and (sender != lastrecipient and amount != lastamount):
                    if sender == lastsender and not throttle:

                        throttle = True
                        api.PostUpdate(sender + " is sending many big payments!! Check them out!")
                    else:
                        throttle = False
                        if amount >= 1_000_000:
                            tweet = sender[:16] + "... sent " + str(amount) + " $BAN to " + recipient[:16] + "...\nThe lambo has arrived" + "\nBlock: " + "https://creeper.banano.cc/explorer/block/" + block
                            if lastTweet != tweet:
                                api.PostUpdate(tweet)
                        elif amount >= 500_000:
                            tweet = sender[:16] + "... sent " + str(amount) + " $BAN to " + recipient[:16] + "...\nThey're going on holiday!!!" + "\nBlock: " + "https://creeper.banano.cc/explorer/block/" + block
                            if lastTweet != tweet:
                                api.PostUpdate(tweet)
                        elif amount >= 100_000:
                            tweet = sender[:16] + "... sent " + str(amount) + " $BAN to " + recipient[:16] + "...\nThis is a party!!" + "\nBlock: " + "https://creeper.banano.cc/explorer/block/" + block
                            if lastTweet != tweet:
                                api.PostUpdate(tweet)
                        elif amount >= 50_000:
                            tweet = sender[:16] + "... sent " + str(amount) + " $BAN to " + recipient[:16] + "...\nMaybe it's drugs!" + "\nBlock: " + "https://creeper.banano.cc/explorer/block/" + block
                            if lastTweet != tweet:
                                api.PostUpdate(tweet)
                lastsender = sender
                lastrecipient = recipient
                lastamount = amount

    except KeyboardInterrupt:
        print("\nShutting down...\n")
    except Exception as exc:
        tweet = "I fell over! :( Ping my owner to check on me"
        serversocket.close()
        if lastTweet != tweet:
            api.PostUpdate(tweet)
        print("Error:\n")
        print(exc, time.ctime())
        time.sleep(300)
        createServer()

    serversocket.close()

print('Access http://localhost:13345')
createServer()
