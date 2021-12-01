import os
import json
import discord
from dotenv import load_dotenv
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()


# loading data
json_file = open('data.json')
json_str = json_file.read()
weight_database = json.loads(json_str)


def is_float(weight_string):
    try:
        float(weight_string)
        return True
    except ValueError:
        return False


async def update_weight(user_id, new_weight, channel_id):
    current_date_obj = datetime.today()
    
    if user_id not in weight_database:  # first time tracking weight
        weight_database[user_id] = {  # prefill with empty weights
            "date_started": current_date_obj.strftime('%d-%m-%Y'),
            "weights": {}
        }

    user_data = weight_database[user_id]  # grab isolated user data so you dont mess with other data
    
    user_start_date_obj = datetime.strptime(user_data["date_started"], '%d-%m-%Y')
    days_since_start = str((current_date_obj - user_start_date_obj).days)

    user_data["weights"][days_since_start] = new_weight
    print(user_data["weights"])

    await graph_weight(user_id, channel_id)

    # save new data in json file
    with open('data.json', 'w') as fp:
        json.dump(weight_database, fp,  indent=4)

    
async def graph_weight(user_id, channel_id):
    user_data = weight_database[user_id]
    x = list(user_data["weights"].keys())
    x = list(map(int, x))  # convert strings to ints
    y = list(user_data["weights"].values())
    
    plt.figure(figsize=(12, 6))
    sns.set_style("darkgrid")
    sns.lineplot(x=x, y=y, marker="o", color="turquoise")

    username = await client.fetch_user(user_id)
    plt.title(username)
    plt.xlim(0)
    plt.xlabel('Days since ' + user_data["date_started"])
    plt.ylabel('Weight')
    plt.savefig("temporary_graph.png")
    plt.close()

    # Post image as message
    target_channel = client.get_channel(int(channel_id))
    await target_channel.send(file=discord.File('temporary_graph.png'))


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    if message.author == client.user:  # ignore all commands if its the bot itself doing it
        return None

    msg = message.content.split()
    user_id = str(message.author.id)

    if len(msg) == 2 and msg[0] == 'tw' and is_float(msg[1]):
        print("Updating weight for " + user_id + ": " + str(msg[1]))
        channel_id = str(message.channel.id)
        await update_weight(user_id, float(msg[1]), channel_id)


client.run(TOKEN)
