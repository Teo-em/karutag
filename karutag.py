import discord


from src.constant import PATH_DATA
from src.constant import PATH_SCRIPT
from src.constant import PATH_TEMP
from src.constant import TOKEN

import os.path
import requests
import subprocess



def run_command(command):
    return subprocess.run(command.split(), capture_output=True, text=True, universal_newlines=True).stdout


def run_script(script, params=""):
    command = PATH_SCRIPT + script
    if params:
        command += " " + params
    return run_command(command)


def get_user(self, name):
    if name.startswith("<@"):
        user = self.get_user(int(name[2:-1]))
    else:
        user = discord.utils.get(self.get_all_members(), name=name)
    return user


async def print_help(self, message):
    await message.channel.send(run_command("cat " + PATH_DATA + "help.txt"))



async def raw_run(self, message):
    if message.author.id == 305483295833980938:
        command = ' '.join(message.content.split()[1:])
        response = run_command(command)
        if response:
            await message.channel.send(response)
        return


async def karuta_cards(self, message):
    if message.attachments:
        for attachment in message.attachments:
            image_url = attachment.url
            response = requests.get(image_url)            
            with open(PATH_TEMP+'card.webp', 'wb') as file:
                file.write(response.content)
        await message.channel.send(run_script("extract.sh"))


def temp_user_path(user_id):
    return PATH_TEMP+str(user_id)+".txt"

def temp_user_exists(user_id):
    return os.path.isfile(temp_user_path(user_id))


async def karuta_init(self, message):
    user_id = message.author.id
    if temp_user_exists(user_id):
        await message.channel.send("Ya existe una sesion para <@"+str(user_id)+">.")
        return
    with open(temp_user_path(user_id), 'w') as file:
        file.write("")
    await message.channel.send("Hecho.")


async def karuta_end(self, message):
    user_id = message.author.id
    if not temp_user_exists(user_id):
        await message.channel.send("No existe una sesion para <@"+str(user_id)+">.")
        return

    await message.channel.send(file=discord.File(temp_user_path(user_id)))
    run_command("rm "+temp_user_path(user_id))


async def karuta_save(self, message):
    if not message.embeds:
        return
    content = message.embeds[0].description
    if not content.startswith("Cards owned by <@"):
        return
    string_length = len("Cards owned by <@")
    user_id = content[string_length:string_length+18]
    if not temp_user_exists(user_id):
        return
    content = content.splitlines()[2:]
    result = ""
    for code in content:
        result += code.split("`")[1].strip()+" "
    with open(temp_user_path(user_id), 'a') as file:
        file.write(result)


commands = {
    "exec": [raw_run],

    
    "ktg help": [print_help],
    "karutag help": [print_help],
    "ktg init": [karuta_init],
    "ktg end": [karuta_end],
    "karutag init": [karuta_init],
    "karutag end": [karuta_end],
}


class TomCat(discord.Client):

    async def on_ready(self):
        print(f'A darle atomos! {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        
        if message.author.id == 646937666251915264:
            await karuta_save(self, message)
            return


        for prefix, functions in commands.items():
            if message.content.lower().startswith(prefix):
                for function in functions:
                    await function(self, message)
                break


    async def on_message_edit(self, before, after):
        if before.author.id == 646937666251915264:             
            await karuta_save(self, after)


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = TomCat(intents=intents)
client.run(TOKEN)
