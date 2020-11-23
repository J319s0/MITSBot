import asyncio
import os
import datetime
import discord
import requests
from discord.ext import commands, tasks
from bs4 import BeautifulSoup

token = 'xxx'
os.chdir('xxx')
client = discord.Client()

# Create MITS Bot help embed
helpEmbed = discord.Embed(
                description = '_ _\n_ _\n',
                colour = discord.Colour(0xbe2a36)
            )
helpEmbed.set_author(name="MITSBot Commands", icon_url="https://cdn.discordapp.com/emojis/756060351854018610.png")
helpEmbed.add_field(name='<:student:780271578608828437> __**Student Commands**__', value='\
    `m!resources` Get study and support resources.', inline=False)
helpEmbed.add_field(name='_ _', value='_ _', inline=True) # Gap between command sections
helpEmbed.add_field(name='<:birthday:779924273950490646> __**Birthday Commands**__', value=' \
    `m!addbday [Month] [Day]` Register a birthday. E.g. m!addbday January 1\n\
    `m!delbday` Remove a birthday.\n\
    `m!viewbday` View today\'s birthdays.', inline=False)
    
# Create Murdoch resources embed
resourcesEmbed = discord.Embed(
                title = '<:student:780271578608828437><:student:780271578608828437> Murdoch Resources <:student:780271578608828437><:student:780271578608828437>',
                description = '_ _\n_ _\n',
                colour = discord.Colour(0xbe2a36)
            )
resourcesEmbed.add_field(name='<:book:780285717124743168> Studying', value=' \
    [myMurdoch Learning](https://moodleprod.murdoch.edu.au/my/)\n\
    [Murdoch Library](https://www.murdoch.edu.au/library)\n\
    [Murdoch Referencing](https://www.murdoch.edu.au/library/help-support/support-for-students/referencing)\n\
    [Study Resources](https://moodleprod.murdoch.edu.au/course/view.php?id=9416#section-6)\n\
    [Murdoch Bookshop](https://our.murdoch.edu.au/Bookshop/)\n\
    [Student Hub Booking](https://studenthub.libcal.com/)')
resourcesEmbed.add_field(name='_ _', value='_ _', inline=True) # Limits embed to two columns
resourcesEmbed.add_field(name='<:question:780285635021897729> Course Help', value=' \
    [Murdoch Handbook](https://handbook.murdoch.edu.au/)\n\
    [Dates and Timetables](https://timetables.murdoch.edu.au/)\n\
    [myMurdoch Advice](https://www.murdoch.edu.au/mymurdoch/support-advice/mymurdoch-advice)\n\
    [Academic Contacts](https://www.murdoch.edu.au/contacts/academic/)')
resourcesEmbed.add_field(name='_ _', value='_ _', inline=False) # Gap between resources sections
resourcesEmbed.add_field(name='<:computer:780285373959634984> Student Software', value=' \
    [Azure Dev Tools](https://azureforeducation.microsoft.com/devtools)\n\
    [GitHub Developer Pack](https://education.github.com/pack)\n\
    [VMware Academy](https://e5.onthehub.com/WebStore/ProductsByMajorVersionList.aspx?ws=ef64204f-8ec4-de11-886d-0030487d8897&vsro=8)')
resourcesEmbed.add_field(name='_ _', value='_ _', inline=True) # Limits embed to two columns
resourcesEmbed.add_field(name='<:briefcase:780285263585738815> Jobs and Internships', value=' \
    [GradConnection](https://au.gradconnection.com/graduate-jobs/information-technology/)\n\
    [GradAustralia](https://gradaustralia.com.au/)')
resourcesEmbed.add_field(name='_ _', value='_ _', inline=False) # Gap between resources sections
resourcesEmbed.add_field(name='<:person_raising_hand:780285082228228116> Support', value=' \
    [Murdoch Support Services](https://www.murdoch.edu.au/life-at-murdoch/support-services)\n\
    [Murdoch Counselling](https://www.murdoch.edu.au/counselling)\n\
    [Murdoch Doctor](http://www.murdoch.edu.au/Medical/Making-an-appointment/)\n\
    [Mental Health Helplines](https://www.healthdirect.gov.au/mental-health-helplines)\n\
    [Headspace](https://headspace.org.au/)')

# Filter deals that contain a blacklisted keyword
def FilterDeal(deal):
    filterList = ["Alienware", "Vacuum", "Blender", "Coffee", "Washer", "Washing Machine", "Fryer", "Battery", "Batteries", "Lamp", "Mower", "Barista", "Shaver", "Purifier", "Camera"] 
    for filter in filterList:
        if  (filter.lower() in deal.lower()):
            return True
    return False

# Scrape url for new deals
def CheckURL(url, file, otherFile):
    # Fetch deals from first history file
    f = open(file, "r")
    dealHistory = f.readlines()
    f.close()

    # Reduce size of first deals history file (if over 60 lines)
    if (len(dealHistory) > 60):
        f = open(file, "w")
        newHistory = dealHistory[10:]
        for line in newHistory:
            f.write(line)
        f.close()
 
    # Fetch deals from second history file
    f = open(otherFile, "r")
    dealHistory = dealHistory + f.readlines()
    f.close()

    newDeals = []

    # Retrieve new deals and extract their information
    data = requests.get(url)
    html = BeautifulSoup(data.text, 'html.parser')
    rawPosts = html.select('div[class^="node node-ozbdeal node-teaser"]')
    rawTitles = html.select('h2.title')
    dealEmbeds = []
    
    # Iterate through deals
    for i in range(len(rawTitles)):
        aElement = rawTitles[i].find('a', href=True)
        dealLink = aElement['href']
        refinedDealLink = '<https://www.ozbargain.com.au' + dealLink + '>'

        # Check if deal has already been posted, or contains a restricted keyword
        if (str(dealLink + '\n') in dealHistory):
            continue
        elif (FilterDeal(aElement.text) is True):
            continue

        else:
            titleVar = aElement.text
            if ('@' in titleVar):
               atLocation = titleVar.find('@')
               titleVar = titleVar[:atLocation]
            store = rawPosts[i].find('span', {'class': 'via'}).find('a', href=True).text
            foxshot = rawPosts[i].find('div', {'class': 'foxshot-container'})
            imageLink = foxshot.find('img')['src']
            couponCode = rawPosts[i].find('div', {'class': 'couponcode'})
            if (couponCode is None):
                couponCode = 'N/A'
            else:
                couponCode = couponCode.text
            externalLink = '<https://www.ozbargain.com.au' + foxshot.find('a', href=True)['href'] + '>'
            
            # Create new Discord embed message, and add it to the new deals list
            embed = discord.Embed(
                title = titleVar,
                description = '_ _\n_ _\n',
                colour = discord.Colour(0xbe2a36)
            )
            embed.set_thumbnail(url=imageLink)
            embed.add_field(name='Store', value=store)
            embed.add_field(name='Coupon Code', value=couponCode)
            embed.add_field(name='_ _', value='_ _', inline=False)
            embed.add_field(name='OzBargain Link', value='[Here]('+refinedDealLink+')')
            embed.add_field(name='Deal Link', value='[Here]('+externalLink+')')
            newDeals.append(dealLink)
            dealEmbeds.append(embed)
            print ("Found new deal: " + str(dealLink))
    
    # Append new deals to the relevant deals history file
    f = open(file, "a")
    for newDeal in newDeals:
        f.write(newDeal + '\n')
    f.close()
    return dealEmbeds
      
@tasks.loop(minutes=1)
async def checkForDeals():
    dealEmbeds = CheckURL('https://www.ozbargain.com.au/cat/computing', 'computing.txt', 'electronics.txt')
    print ("Checked for new computing deals.")
    for embedVar in dealEmbeds:
        await bargainChannel.send(embed=embedVar)
    await asyncio.sleep(60)

    dealEmbeds = CheckURL('https://www.ozbargain.com.au/cat/electrical-electronics', 'electronics.txt', 'computing.txt')
    print ("Checked for new electronics deals.")
    for embedVar in dealEmbeds:
        await bargainChannel.send(embed=embedVar)

def getBdays():
    f = open("birthdays.txt", "r")
    birthdays = f.readlines()
    f.close()
    return birthdays
  
def getTodaysBirthdays():
    todaysBirthdays = []
    birthdaysEmbed = 0
    today = datetime.datetime.today()
    today = today.strftime("%B %d")
    
    birthdays = getBdays()
    for birthday in birthdays:
        birthdaydate = birthday[19:]
        if (today in birthdaydate):
            todaysBirthdays.append(birthday[:18])
            
    if (len(todaysBirthdays) != 0):
        embedDesc = '_ _\n'
        for birthday in todaysBirthdays:
            embedDesc += 'It\'s <@' + birthday + '>\'s birthday today!\n'
        embedDesc += '\nHappy Birthday!\n'
        birthdaysEmbed = discord.Embed(
            description = embedDesc,
            title = '<:birthday:779924273950490646><:birthday:779924273950490646> Today\'s Birthdays <:birthday:779924273950490646><:birthday:779924273950490646>',
            colour = discord.Colour(0xbe2a36)
        )
        
    return birthdaysEmbed
    
# Check if a user ID exists in the birthdays file
def birthdayExists(userID):
    birthdays = getBdays()
    for birthday in birthdays:
        if (userID in birthday):
            return True
    return False

async def addBday(message):
    userID = str(message.author.id)
    if (birthdayExists(userID)):
        await message.channel.send("Your birthday is already registered. To remove and re-submit your birthday, try using m!help.")
        return
    try:
        birthday = datetime.datetime.strptime(message.content[10:], '%b %d')
    except:
        try:
            birthday = datetime.datetime.strptime(message.content[10:], '%B %d')
        except:
            await message.channel.send("That wasn't quite right. Try using m!help to find the right command.")
            return
    f = open('birthdays.txt', "a")
    f.write(userID + ' ' + str(birthday.strftime("%B %d")) + '\n')
    f.close()
    await message.channel.send("Your birthday has been registered.")
    return
    
async def delBday(message):
    userID = str(message.author.id)
    if (not birthdayExists(userID)):
        await message.channel.send("Your birthday hasn't been registered yet. Try using m!help to register your birthday first.")
        return
    birthdays = getBdays()
    f = open('birthdays.txt', "w")
    for birthday in birthdays:
        if (userID not in birthday):
            f.write(birthday)
    f.close()
    await message.channel.send("Your birthday has been deleted.")
    return
    
async def viewBday(message):
    todaysBirthdays = getTodaysBirthdays()
    if (todaysBirthdays != 0):
        await message.channel.send(embed=todaysBirthdays)
    else:
        await message.channel.send("It's nobody\'s birthday today :(")

@client.event
async def on_message(message):
    # Check if message came from bot
    if (message.author == client.user):
        return
    
    # Check if message is a bot command
    if (message.content.lower().startswith("m!")):
        command = message.content.lower()[2:]
        
        # Check what the command is, and respond accordingly
        if (command.startswith("addbday")):
            await addBday(message)
            return
        elif (command.startswith("delbday")):
            await delBday(message)
            return
        elif (command.startswith("help")):
            await message.channel.send(embed=helpEmbed)
        elif (command.startswith("viewbday")):
            await viewBday(message)
            return
        elif (command.startswith("resources")):
            await message.channel.send(embed=resourcesEmbed)
        else:
            await message.channel.send("That's not a valid command. Try using m!help to find the right command.")

# Check birthdays file each day, and post if any are on the current date
@tasks.loop(hours=24)
async def dailyBirthdays():
    todaysBirthdays = getTodaysBirthdays()
    if (todaysBirthdays != 0):
        await trashcanChannel.send(embed=todaysBirthdays)

# After Discord client is ready, define the channels and start the threads
@client.event
async def on_ready():
    print ('Discord Client ready!')
    
    global trashcanChannel
    global bargainChannel
    trashcanChannel = client.get_channel(xxx)
    bargainChannel = client.get_channel(xxx)
    
    checkForDeals.start()
    
    # Wait until 8AM to post the first birthday(s)
    now = datetime.datetime.now()
    if (int(now.hour) < 8):
        future = now.replace(hour=8, minute=0, second=0, microsecond=0)
    else:
        future = now.replace(hour=8, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
    secondsLeft = int(future.strftime('%s')) - int(now.strftime('%s'))
    await asyncio.sleep(secondsLeft)
    
    dailyBirthdays.start()

client.run(token)
