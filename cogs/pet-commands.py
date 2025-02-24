from datetime import date, datetime, timedelta
import random
from turtle import update
import discord
from discord.ext import commands, tasks

# Falls du fetch_profile_data nutzt, importiere es hier.
from bot_util import load_items, make_embed, get_messages, get_messages_mood
from utilities.profile import show_pet_profile
from utilities.commands import isAOwner
from mongodb.owner import get_all_owner, get_owner
from mongodb.pet import nicknamePet, update_pet
from utilities.pet_interaction import drinkView, feedView, itemView

subgroup = "pet_"
discord_pet_channel = 1343215062197862460
class Pet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_pets_status.start()
    
    @discord.slash_command(name=subgroup+"profile",description="Shows Pet Profiles")
    async def petProfile(self, ctx: discord.ApplicationContext):
        user_data = await isAOwner(ctx.author.id,ctx)
        if not user_data:
            return
        await show_pet_profile(ctx,user_data) 
        
    @discord.slash_command(name=subgroup+"nickname",description="Name your pet :D")
    async def petNickname(self, ctx: discord.ApplicationContext, nickname:str):
        user_data = await isAOwner(ctx.author.id,ctx)
        if not user_data:
            return
        result = nicknamePet(user_data["user_id"], nickname) 
        if result == 0:
            await ctx.response.send_message(embed=make_embed("Naming Failed"), ephemeral=True)
        await ctx.response.send_message(embed=make_embed("Your pet is now called "+nickname))
        
    @discord.slash_command(name=subgroup+"feed",description="Feed your pet :D")
    async def feed(self, ctx: discord.ApplicationContext):
        actionCategory = "eat"
        user_data = await isAOwner(ctx.author.id,ctx)
        if not user_data:
            return
        #action refusal
        pet = user_data["pet"][0]
        logs = pet["logs"]
        if logs.get(actionCategory):
            if (datetime.fromtimestamp(logs[actionCategory]["timestamp"]) + timedelta(minutes=10))>= datetime.now():
                await ctx.response.send_message(embed=make_embed(f"{pet["nickname"]} is not ready to consider eating food."), ephemeral=True)
                return
            elif pet["personality"]["action_resistence"].get(actionCategory):
                if random.randint(0,100)<pet["personality"]["action_resistence"][actionCategory]:
                    pet["logs"][actionCategory]["timestamp"] = int(datetime.now().timestamp)
                    await ctx.response.send_message(embed=make_embed(f"{pet["nickname"]} is refusing to eat", f"{pet["nickname"]} has a mind of it's own and is not wishing to eat yet. You will have to wait 10min until it's more willing to eat."))
                    return
                
        await feedView(ctx, user_data)    
    @discord.slash_command(name=subgroup+"drench",description="Give your pet something to drink :D")
    async def drench(self, ctx: discord.ApplicationContext):
        actionCategory = "drink"
        user_data = await isAOwner(ctx.author.id,ctx)
        if not user_data:
            return
        #action refusal
        pet = user_data["pet"][0]
        logs = pet["logs"]
        if logs.get(actionCategory):
            if (datetime.fromtimestamp(logs[actionCategory]["timestamp"]) + timedelta(minutes=10))>= datetime.now():
                await ctx.response.send_message(embed=make_embed(f"{pet["nickname"]} is not ready to consider eating food."), ephemeral=True)
                return
            elif pet["personality"]["action_resistence"].get(actionCategory):
                if random.randint(0,100)<pet["personality"]["action_resistence"][actionCategory]:
                    pet["logs"][actionCategory]["timestamp"] = int(datetime.now().timestamp)
                    await ctx.response.send_message(embed=make_embed(f"{pet["nickname"]} is refusing to eat", f"{pet["nickname"]} has a mind of it's own and is not wishing to eat yet. You will have to wait 10min until it's more willing to eat."))
                    return
        await drinkView(ctx, user_data)    
    @discord.slash_command(name=subgroup+"hand-over",description="Give your pet an item in your inventory :D")
    async def handOver(self, ctx: discord.ApplicationContext):
        actionCategory = "give"
        user_data = await isAOwner(ctx.author.id,ctx)
        if not user_data:
            return
        #action refusal
        pet = user_data["pet"][0]
        logs = pet["logs"]
        if logs.get(actionCategory):
            if (datetime.fromtimestamp(logs[actionCategory]["timestamp"]) + timedelta(minutes=10))>= datetime.now():
                await ctx.response.send_message(embed=make_embed(f"{pet["nickname"]} is not ready to consider drinking."), ephemeral=True)
                return
            elif pet["personality"]["action_resistence"].get(actionCategory):
                if random.randint(0,100)<pet["personality"]["action_resistence"][actionCategory]:
                    pet["logs"][actionCategory]["timestamp"] = int(datetime.now().timestamp)
                    await ctx.response.send_message(embed=make_embed(f"{pet["nickname"]} is refusing to drink", f"{pet["nickname"]} has a mind of it's own and is not wishing to drink yet. You will have to wait 10min until it's more willing to eat."))
                    return
                
        await itemView(ctx, user_data)
    @discord.slash_command(name=subgroup+"sleep",description="Make it sleep! :D")
    async def sleep(self, ctx: discord.ApplicationContext):
        actionCategory = "sleep"
        user_data = await isAOwner(ctx.author.id,ctx)
        if not user_data:
            return
        #action refusal
        pet = user_data["pet"][0]
        logs = pet["logs"]
        if logs.get(actionCategory):
            if (datetime.fromtimestamp(logs[actionCategory]["timestamp"]) + timedelta(minutes=10))>= datetime.now():
                await ctx.response.send_message(embed=make_embed(f"{pet["nickname"]} is not ready to consider sleeping."), ephemeral=True)
                return
            elif pet["personality"]["action_resistence"].get(actionCategory):
                if random.randint(0,100)<pet["personality"]["action_resistence"][actionCategory]:
                    pet["logs"][actionCategory]["timestamp"] = int(datetime.now().timestamp)
                    await ctx.response.send_message(embed=make_embed(f"{pet["nickname"]} is refusing to sleep", f"{pet["nickname"]} has a mind of it's own and is not wishing to sleep yet. You will have to wait 10min until it's more willing to eat."))
                    return
                
        pet["is_sleeping"] = True
        await ctx.response.send_message(embed=make_embed(f"{pet["nickname"]} goes to sleep", f"{pet["nickname"]} goes to it's bed and curls up. Sleeping peacefully until you wake it or it is 100%"))
        update_pet(user_data["user_id"], pet)
    
    @tasks.loop(minutes=10)
    async def update_pets_status(self):
        # get all users
        owners = get_all_owner()
        if not owners:
           channel = self.bot.get_channel(1054381452252426260)
           if channel:
                #await channel.send(f"<@{470689466307313664}>. Hey. I got issues getting the Owner List. Could you fetch it for me?")
                return
        # get pets
        for owner in owners:
            # messages
            title = ""
            description = ""
            pet = owner["pet"][0]
            # check if alive even
            if pet["died"]:
                continue
            # go around moods
            list = ["happiness","intelligence","health","hunger","thirst","energy"]
            #get type buff/debuff
            for stat in list:
                # 20% not changed
                chance = random.randint(0, 10)
                if chance in [4,9]:
                    continue
                # change - 1*buff/debuff*moodEffect*sicknessEffect
                # get typing buff
                typeEffect = pet["typeEffects"].get("fast", {}).get(stat, 1)
                if typeEffect == 1:
                    typeEffect = pet["typeEffects"].get("slow", {}).get(stat, 1) 
                #sickness
                sicknessDebuff = pet["sick"]
                if sicknessDebuff != None:
                    if sicknessDebuff["name"] != "Dying":
                        sicknessDebuff = pet["sick"].get("effect").get(stat,1)
                    else: sicknessDebuff = 1
                else: sicknessDebuff = 1
                
                # sleep makes energy up. :3
                if pet["is_sleeping"] and stat == "energy":
                    pet[stat] =  round(pet[stat] +(2 * typeEffect), 1)
                    if pet[stat] >= 100:
                        pet[stat] == 100
                        # send notification pet woke up.
                        title = f"{pet["nickname"]} woke up from it's nappy :sparkles:"
                        # wake pet up
                        pet["is_sleeping"] = not pet["is_sleeping"]
                        description += get_messages("woken", pet["nickname"])
                    continue
                pet[stat] = round(pet[stat] -(1 * typeEffect * pet["mood"]["generalBuff"][stat] * sicknessDebuff), 1)
                pet[stat] = max(0, min(100, pet[stat]))
                # Consider Personality tendency...
                # energy <0 passing out - very unhappy mood when waking up and -30 happiness
                if stat == "energy" and pet[stat] <=0:
                    pet["is_sleeping"] = not pet["is_sleeping"]
                    pet["happiness"] -= 20
                    title = f"{pet["nickname"]} has passed out..."
                    description += get_messages("fainting",pet["nickname"])
                    continue
            # mood changes and algorythm
            result = self.update_pet_mood(owner,pet,list)
            # died
            update_pet(owner["user_id"], pet)
            if result["status"]==0:
                title = f"{pet["nickname"]} has taken it's final breath... ⚰️"
                description +=f"<@{owner["user_id"]}>. {result["message"]}" 
                channel = self.bot.get_channel(discord_pet_channel)
                if channel:
                    await channel.send(embed=make_embed(title,description))
                continue
            elif result["message"]== "":
                continue
            else:
                title = f"{pet["nickname"]} gives you a little update! :sparkles:"
                description += result["message"]
                # send notificications if is on
                if owner["notifications"] != "none":
                    user = await self.bot.fetch_user(owner["user_id"])
                    # Sending a direct message to the user
                    await user.send(embed=make_embed(title,description))
            
    def update_pet_mood(self,owner,pet, statList):
        description = ""
        moodscription ="**Mood Change:**\n"
        logs = pet.get("logs")
        if not logs:
            pet.setdefault("logs", {}).setdefault("long_mood", {"timestamp": 0, "range": 0})
            logs = pet["logs"]
                
        # when can range mood be overwriten? 
            # When sick
            # when low
            # only needs overwriting when not the same mood in there
        result = self.update_sickness(pet,logs)
        if result["status"]==0:
            return result
        description += result["message"]
        personalities = load_items("personalities.json")
        personality = personalities[pet["personality"]["name"]]
        moodsList = load_items("emotion.json")
        # check if mood changes for sickness
        if result["status"] == 1:
            if  pet["mood"]["name"] in personality["sick_tendency"]:
                return {"status":1,"message":description}
            for sick_mood in personality["sick_tendency"]:
                if random.randint(0,100)<personality["sick_tendency"][sick_mood]:
                    pet["mood"]= moodsList[sick_mood]
                    moodscription += get_messages_mood("got_sick",pet["nickname"], sick_mood,pet["sick"]["name"])
                    return {"status":1,"message":(description+moodscription)}
                
        # check if mood changes for low <30
        for stat in statList:
            if pet[stat]<=25:
                if  pet["mood"]["name"] in [mood["name"] for mood in personality["low_tendency"]]:
                    return {"status":1,"message":description}
                for low_mood in personality["low_tendency"]:
                    if random.randint(0,100)<low_mood["chance"]:
                        pet["mood"]= moodsList[low_mood["name"]]
                        moodscription += f"-# Mood changed because of low {stat}\n"
                        moodscription += get_messages_mood("low_"+stat,pet["nickname"], low_mood["name"])
                        return {"status":1,"message":(description+moodscription)}
        # check if mood change generally
        long_mood_chance = random.randint(0,100) <= 20
        mood_change_change = random.randint(0,100) <= 45
        
        if not mood_change_change:
            return {"status":1,"message":description}
        
        if logs["long_mood"]["timestamp"] !=0:
            if (datetime.fromtimestamp(logs["long_mood"]["timestamp"]) + timedelta(minutes=logs["long_mood"]["range"]))>= datetime.now():
                return {"status":1,"message":description}
        #See if a tendency is choosen
        for mood_tendency in personality["mood_tendency"]:
            if random.randint(0,100)<mood_tendency["chance"]:
                pet["mood"]= moodsList[mood_tendency["name"]]
                if long_mood_chance and any(moodTime["name"] == mood_tendency["name"] for moodTime in personality["mood_time"]):
                    logs["long_mood"]["timestamp"] = int(datetime.now().timestamp())
                    logs["long_mood"]["range"] = next(
                        (random.randint(moodTime["range"][0], moodTime["range"][1]) 
                        for moodTime in personality["mood_time"] 
                        if moodTime["name"] == mood_tendency["name"]),
                        None  # Default value if no match is found
                    )
                    pet["logs"] = logs
                    moodscription += get_messages_mood("long_mood",pet["nickname"], mood_tendency["name"])
                    if owner["notifications"]=="normal":
                        return {"status":1,"message":(description+moodscription)}
                    return {"status":1,"message":description}
                else:
                    logs["long_mood"]["timestamp"] = 0
                    logs["long_mood"]["range"] = 0
                pet["logs"] = logs
                moodscription += get_messages_mood("new_mood",pet["nickname"], mood_tendency["name"])
                if owner["notifications"]=="normal":
                    return {"status":1,"message":(description+moodscription)}
                return {"status":1,"message":description}
                
        # No tendency? Guess its time for the other moods :D
        tendency_names = [mood["name"] for mood in personality["mood_tendency"]]
        new_mood_list = {key: value for key, value in moodsList.items() if key not in tendency_names}
        pet["mood"] = new_mood_list[random.choice(list(new_mood_list.keys()))]
        pet["logs"] = logs
        moodscription += get_messages_mood("new_mood",pet["nickname"], pet["mood"]["name"])
        if owner["notifications"]=="normal":
            return {"status":1,"message":(description+moodscription)}
        return {"status":1,"message":description}
                
    def update_sickness(self, pet, logs):
        if not logs.get("sick"):
            logs.setdefault("sick", {"timestamp": 0, "range": 0})
        description = "**Sickness: \n**"
        sicknesses = load_items("sickness.json")
        sicknesses = [
            s for s in sicknesses
            if s.get("triggers") and any(key in s["triggers"] for key in ["eat", "drink", "happy"])
        ]
        # check if already dying then kill it it.
        if pet["sick"]:
            if pet["sick"]["name"]=="Dying":
                if (datetime.fromtimestamp(logs["dying"]) + timedelta(minutes=30)) <= datetime.now() and pet["health"] == 0:
                    pet["died"]= int( datetime.now().timestamp())
                    death = get_messages("death",pet["nickname"])
                    return {"status":0, "message":death}
        # <0 adds dying - food/drinky
        if pet.get("hunger",1)<=0 or pet.get("thirst",1)<=0:
            dying_sickness = next((s for s in sicknesses if s["name"] == "Dying"), None)
            if not pet.get("sick"):
                pet["sick"] = dying_sickness
                logs["dying"] = int( datetime.now().timestamp())
                return {"status":1, "message":description + get_messages("sick",pet["nickname"],pet["sick"]["name"])}
            if pet["sick"]["name"] != dying_sickness["name"]:
                pet["sick"] = dying_sickness
                logs["dying"] = int( datetime.now().timestamp())
                return {"status":1, "message":description + get_messages("sick",pet["nickname"], pet["sick"]["name"])}
            return {"status":1, "message":""}
        
        ### already is sick and cant get another
        if (datetime.fromtimestamp(logs["sick"]["timestamp"]) + timedelta(minutes=logs["sick"]["range"]))>= datetime.now():
            return {"status":2, "message":""}
        
        food_sicknesses = []

        ## collect sicknesses food and happy related
        for sickness in sicknesses:
            if any(key in sickness["triggers"] for key in ["happy", "eat", "drink"]):
                if sickness["triggers"]["operator"] == "below":
                    if pet["hunger"] <= sickness["triggers"].get("eat",100) or pet["thirst"] <= sickness["triggers"].get("drink",100) or pet["happiness"] <= sickness["triggers"].get("happy",100):
                        food_sicknesses.append(sickness)                             
                else:
                    if pet["hunger"] >= sickness["triggers"].get("eat",0) or pet["thirst"] >= sickness["triggers"].get("drink",0) or pet["happiness"] >= sickness["triggers"].get("happy",0):
                        food_sicknesses.append(sickness)
        ## which have the chance to be used
        sickness_possibility = []
        if food_sicknesses:
            for sick in food_sicknesses:
                if random.randint(0,100)<= sick["triggers"]["chance"]:   
                    sickness_possibility.append(sick)                 
        ## select a random one who won
        if sickness_possibility:
            pet["sick"] = random.choice(sickness_possibility)
            description += get_messages("sick",pet["nickname"], pet["sick"]["name"])
            logs["sick"]["timestamp"] =  int(datetime.now().timestamp())
            logs["sick"]["range"] = random.randint(pet["sick"]["range"][0],pet["sick"]["range"][1])
            return {"status":1, "message":description}
        else:
            return {"status":2, "message":""}
    
        


def setup(bot):
    bot.add_cog(Pet(bot))
