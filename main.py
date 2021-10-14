#importing libraries
import discord
from discord.ext import commands, tasks

import os
import random
from replit import db

import datetime, time
import dateparser

import asyncio
from asyncio import sleep


client = discord.Client()

taskIds = {}
alarm_list = ['']
taskAndDeadline = {"testtask":""}
taskAndReminder = {"testtask":""}


@client.event
async def on_ready():
  remind_Ppl.start()
  print('We have logged in as {0.user}'.format(client))
  

@tasks.loop(seconds = 10) #gives alarm when the duedate comes
async def remind_Ppl():
    await client.wait_until_ready()
    while not client.is_closed():
        now = str(dateparser.parse('now').replace(second=0, microsecond=0))

        for key in taskAndDeadline: #key will be a task
            if str(now) == str(taskAndDeadline[key]): #if time = time
                channel = client.get_channel(820314689178304553)
                await channel.send('Did you do the task: ' + str(key) +'?')
                thetime = 60
            else:
                thetime = 60

        for key in taskAndReminder: #key will be a task
            if str(now) == str(taskAndReminder[key]): #if time = time
                channel = client.get_channel(820314689178304553)
                await channel.send('REMINDER! Please do task: ' + str(key))
                thetime = 60
            else:
                thetime = 60
        await asyncio.sleep(thetime)


@client.event
async def on_message(message):

##--- Tasks Functions --- ##
  msg = message.content

  def add_task(task):
      if(task in db.keys()): #task already created
        return 0
      else:
        db[task] = {}
        return 1

  def del_task(task):
    if(task in db.keys()): #task exists
      del db[task]
      return 1
    else:
      return 0

  if msg.startswith("-addtask"):
    task = msg.split("-addtask ",1)[1]
    if(add_task(task) == 0):
       await message.channel.send("Task with that name already exists")
    else:
      await message.channel.send("Task added!")
      
  
  if msg.startswith("-fulltask"):
    fulltext = msg.split("-fulltask ",1)[1] #gets entire text withouth ctx
    nomention = fulltext.split(" <",1)[0] #removes mentions
    task = fulltext.split(": ",1)[0] #
    duedate = nomention.split(": ",1)[1]


    parsedDate = dateparser.parse(duedate)
    if (parsedDate != None):
          if (parsedDate < datetime.datetime.now()):
              theDate = parsedDate.replace(second=0, microsecond=0)+datetime.timedelta(days=7)

          else:
              theDate = parsedDate.replace(second=0, microsecond=0)

          organizedDate = str(theDate)
          await message.channel.send('The due date is '+ organizedDate)
          alarm_list.append(theDate)
          taskAndDeadline[task] = theDate

    elif ('next' in duedate):
          duedate = duedate.lstrip('next')
          parsedDate = dateparser.parse(duedate)
          if (parsedDate != None):
              if (parsedDate < dateparser.parse('monday')):
                  theDate = parsedDate.replace(second=0, microsecond=0)+datetime.timedelta(days=14)
              else:
                  theDate = parsedDate.replace(second=0, microsecond=0)+datetime.timedelta(days=7)
                  
              organizedDate = str(theDate)
              await message.channel.send('The due date is '+ organizedDate)
              alarm_list.append(theDate)
              taskAndDeadline[task] = theDate
    
          else:
              await message.channel.send('Please enter a valid due date')
    else:
          await message.channel.send('Please enter a valid due date')


    if(add_task(task) == 0):
       await message.channel.send("Task with that name already exists")
    else:
      # tasktext = await message.channel.send("{} was added!".format(task))
      taskList = db[task] 

      members = ""
      for member in message.mentions:
        taskList[(member.id)] = "Not completed" #name, completion
        print(member)
      db[task] = taskList
      print(db[task])
      
      embed = discord.Embed(title="{}".format(task), description="", color=discord.Color.blue())
      embed.add_field(name="Deadline", value="{}".format(taskAndDeadline[task]), inline=True)
      embed.add_field(name="Reminder settings", value="{}".format("Reminder not set"), inline=True)
      tasktext = await message.channel.send(embed=embed)
        # await tasktext.add_reaction("✅")
      taskIds[tasktext.id] = task
      await tasktext.add_reaction("✅")

  if msg.startswith("-deltask"):
    task = msg.split("-deltask ",1)[1]
    if(del_task(task) == 0):
       await message.channel.send("Task with that name does not exist")
    else:
      await message.channel.send("Task deleted")
  
  if msg.startswith("-delall"):
    for task in list(db.keys()):
      del db[task]
    await message.channel.send("All tasks deleted")

  if msg.startswith("-sumtask"):

    if len(list(taskAndDeadline.keys())) != 0:
      tasks = ""
      deadlines = ""


      for task in taskAndDeadline.keys():
        tasks += "{}\n".format(task)
        deadlines += "{}\n".format(taskAndDeadline[task])
      
      embed = discord.Embed(title="Task Summary", description="", color=discord.Color.red())
      embed.add_field(name="Tasks", value="{}".format(tasks), inline=True)
      embed.add_field(name="Deadlines", value="{}".format(deadlines), inline=True)
      await message.channel.send(embed=embed)

    else: 
      await message.channel.send("No tasks created yet")


##--- Members Functions --- ##

  if msg.startswith("-addmember"): 
    fulltext = msg.split("-addmember ",1)[1]
    task = fulltext.split(" <")[0] 
    userId = message.mentions[0].id
    if task in db.keys():
      taskDict = db[task]
      taskDict[userId] = "Not completed" #name, completion
      db[task] = taskDict
      print(db[task])
      await message.reply("<@!{}> has been added to task: {}".format(userId,task))
    else:
      await message.channel.send("That task doesn't exist yet")

    if msg.startswith("-delmember"): 
      fulltext = msg.split("-delmember ",1)[1]
      task = fulltext.split(" <")[0] 
      userId = message.mentions[0].id
      if task in db.keys():
        taskDict = db[task]
        del taskDict[userId]
        db[task] = taskDict
        await message.reply("<@!{}> has been deleted from task: {}".format(userId,task))
      else:
        await message.channel.send("Member not in task")


  if msg.startswith("-memberstat"):
    task = msg.split("-memberstat ",1)[1]
    if task not in db.keys():
      await message.channel.send("That task doesn't exist yet")
    elif len(db[task]) == 0:
      await message.channel.send("Nobody assigned to task yet")
    else: 
      
      members = ""
      statuses = ""

      taskList = db[task]
      for member in taskList:
        members += "<@!{}>\n".format(member)
        statuses += "{}\n".format(taskList[member])


      embed = discord.Embed(title="{} Member Stats".format(task), description="", color=discord.Color.green())
      embed.add_field(name="Members", value="{}".format(members), inline=True)
      embed.add_field(name="Completion Status", value="{}".format(statuses), inline=True)

      await message.channel.send(embed=embed)



  #-------remind ---------#
  if msg.startswith("-setRemind"):
    fulltext = msg.split("-setRemind ",1)[1] #gets entire text withouth ctx
    task = fulltext.split(": ",1)[0] #
    remindTime = fulltext.split(": ",1)[1]
    actualTime = taskAndDeadline[task]

    if (remindTime == '1min'):
          taskAndReminder[task] =  (actualTime - datetime.timedelta(minutes = 1))
    if (remindTime == '10min'):
          taskAndReminder[task] = (actualTime - datetime.timedelta(minutes = 10))
    if (remindTime == '1hr'):
          taskAndReminder[task] =  (actualTime - datetime.timedelta(hours = 1))
    if (remindTime == '1day'):
          taskAndReminder[task] =  (actualTime - datetime.timedelta(days = 1))
    
    await message.channel.send('Honk will remind you ' + str(remindTime)+' before deadline')


    newEmbed = discord.Embed(title="{}".format(task), description="", color=discord.Color.blue())
    newEmbed.add_field(name="Deadline", value="{}".format(taskAndDeadline[task]), inline=True)
    await message.channel.send(embed = newEmbed)


@client.event
async def on_reaction_add(reaction,user):
  emoji = reaction.emoji

  if(emoji == "✅" and user != client.user):
    reactId = reaction.message.id
    task = taskIds[reactId]

    person = str(user.id)
    members = db[task]
    if(person in members.keys()):
      members[person] = "Completed"
      db[task] = members
    else:
      await reaction.message.channel.send("{} has not been added to the task {}".format(user.display_name,task))


client.run(os.getenv('TOKEN'))
