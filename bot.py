import discord,os,json,traceback,datetime,asyncio
from discord.ext import commands, tasks
from random import randint

client = commands.AutoShardedBot(command_prefix='/')

dguild=client.get_guild(721338195781877820)

def get_embed(title, description='', color=0xCCFFFF): 
    return discord.Embed(title=title,description=description,color=color)

def format_perm_by_name(name):
    names = { 'administrator': '관리자', 'add_reactions': '반응 추가하기' }
    try: rst = names[name]
    except KeyError: rst = name
    return rst

def find_missing_perms_by_tbstr(tbstr: str):
    perms = []
    if 'add_reaction' in tbstr: perms.append('add_reactions')
    return perms

@client.event
async def on_ready():
    print("=====login=====")
    print(client.user.name)
    print(client.user.id)
    print("===============")
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Booting.."))
    client.loop.create_task(bg_change_playing())

@client.event
async def on_member_join(member):
    dguild=client.get_guild(721338195781877820)
    await member.add_roles(discord.utils.get(dguild.roles, id=721338195781877823))
    await client.get_channel(721338195786203227).send(embed=get_embed(f"{member.name}님 디대전에 오신걸 환영합니다!",f"현재 서버 인원수는 {len(dguild.members)}명 입니다."))

@client.event
async def on_member_remove(member):
    dguild=client.get_guild(721338195781877820)
    await client.get_channel(721338195786203227).send(embed=get_embed(f"{member.name}님 안녕히 가세요ㅠㅠ",f"현재 서버 인원수는 {len(dguild.members)}명 입니다.",0xFF0000))

@client.event
async def on_command_error(ctx: commands.Context, error: Exception):
    if isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.send(embed=discord.Embed(title="<a:cross:723540374681026612> | 명령어를 조금만 천천히 써주세요!",description='{:.2f}초만 기다려주세요!'.format(error.retry_after),color=0xFF0000))
        return
    elif isinstance(error.__cause__, discord.HTTPException):
        if error.__cause__.code == 50013:
            if ctx.channel.permissions_for(ctx.guild.me).send_messages:
                missings = find_missing_perms_by_tbstr(errstr)
                fmtperms = [format_perm_by_name(perm) for perm in missings]
                embed = discord.Embed(title='<a:no:698461934613168199> | 봇 권한 부족!', description='이 명령어를 사용하는 데 필요한 봇의 권한이 부족합니다!\n`' + '`, `'.join(fmtperms) + '`', color=0xFF0000, timestamp=datetime.datetime.utcnow())
                await ctx.send(embed=embed)
                return
            else:
                embed = get_embed('<a:no:698461934613168199> | 봇 권한 부족!', f"봇에게 **{ctx.channel.name}** 채널에 메세지를 보낼 권한이 없습니다.", 0xFF0000)
                await ctx.author.send(embed=embed)
                return
        elif error.__cause__.code == 50035:
            embed = discord.Embed(title='<a:no:698461934613168199> | 메시지 전송 실패', description='보내려고 하는 메시지가 너무 길어 전송에 실패했습니다.', color=0xFF0000, timestamp=datetime.datetime.utcnow())
            await ctx.send(embed=embed)
            return

@client.event
async def bg_change_playing():
    with open("./config/config.json", "r", encoding='UTF8') as db_json: config = json.load(db_json)
    Botversion = config["Botversion"]
    for v in [f"디스코드 대신 전해드립니다.", "'/도움'로 봇명령어 알아보기",f"디대전봇 V{Botversion}"]: 
        await asyncio.gather(client.change_presence(activity=discord.Game(v)),asyncio.sleep(20))
    await client.get_channel(723178127982854148).edit(name=f"📊ㅣ서버 유저수 : {len(client.get_guild(721338195781877820).members)-3}")
    client.loop.create_task(bg_change_playing())

@client.command(name='도움')
async def _help(ctx):
    await ctx.send(embed=get_embed("📝 | 디대전봇 도움","/노익명 (할말) - 노익명으로 사연을 보냅니다.\n/익명 (할말) - 익명으로 사연을 보냅니다."))

@client.command(name='공지보내')
@commands.has_permissions(administrator=True)
async def _notice(ctx,*,arg):
    await client.get_channel(721338195786203230).send(arg)
    await ctx.send("전송이 완료되었습니다")

@client.command(name='버젼변경')
async def version(ctx,*,arg):
    config["Botversion"] = arg
    await ctx.send(f"changed to {arg}")

@client.command(name='익명')
@commands.cooldown(1, 120, commands.BucketType.user)
async def _chatno(ctx,*,arg):
    msg = await ctx.send(embed=get_embed(
        "정말 메세지를 보내시겠습니까?",
        """이제 당신이 작성한게 익명으로 올라갈 예정이예요!
'디대전봇' 사용 시 <#721338195786203235> 을(를) 확인 했다는 것으로 간주합니다.
메시지를 전송할까요?

Help / 도움말
<a:check:723540353872953366> 을(를) 누르시면 성공적으로 전송됩니다. 
<a:cross:723540374681026612>: 을(를) 누르시면 메시지 전송을 취소합니다."""
        ))
    emjs=['<a:check:723540353872953366>','<a:cross:723540374681026612>']
    await msg.add_reaction(emjs[0])
    await msg.add_reaction(emjs[1])
    def check(reaction, user):
        return user == ctx.author and msg.id == reaction.message.id and str(reaction.emoji) in emjs
    try: reaction, user = await client.wait_for('reaction_add', check=check, timeout=20)
    except asyncio.TimeoutError:
        await asyncio.gather(msg.delete(),ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000)))
        return
    else:
        e = str(reaction.emoji)
        if e == emjs[0]:
            firstemj=['📝', '✏️', '🖋️', '🖊️']
            embed=get_embed(firstemj[randint(0,3)]+f" | **익명 대신 전해드립니다**",">>> ```"+arg+'```')
            amsg=await client.get_channel(721338195962363914).send(embed=get_embed("UPLOADING"))
            await amsg.edit(context=" ",embed=embed.set_footer(text=amsg.id,icon_url=client.user.avatar_url))
            await amsg.add_reaction('<:Love:723450843659239474>')
            await client.get_channel(731643189164900354).send(f"{ctx.author.id} | {ctx.author}\n{amsg.id}")
            await asyncio.gather(msg.delete(),ctx.send("<a:check:723540353872953366> 아무도 모르게 당신의 게시글이 익명으로 올라갔어요!\n게시글 채널을 확인해주세요!"))
        elif e == emjs[1]:
            await asyncio.gather(msg.delete(),ctx.send("전송이 취소되었습니다."))

@client.command(name='댓글')
async def _chatdet(ctx,*,arg):
    amsg = await client.get_channel(731053923971891290).send("> "+arg)
    await amsg.add_reaction('<:Love:723450843659239474>')

@client.command(name='노익명')
@commands.cooldown(1, 120, commands.BucketType.user)
async def _chatyes(ctx,*,arg):
    msg = await ctx.send(embed=get_embed(
        "정말 메세지를 보내시겠습니까?",
        """이제 당신이 작성한게 노익명으로 올라갈 예정이예요!
'디대전봇' 사용 시 <#721338195786203235> 을(를) 확인 했다는 것으로 간주합니다.
메시지를 전송할까요?

Help / 도움말
<a:check:723540353872953366> 을(를) 누르시면 성공적으로 전송됩니다. 
<a:cross:723540374681026612>: 을(를) 누르시면 메시지 전송을 취소합니다."""
        ))
    emjs=['<a:check:723540353872953366>','<a:cross:723540374681026612>']
    await msg.add_reaction(emjs[0])
    await msg.add_reaction(emjs[1])
    def check(reaction, user):
        return user == ctx.author and msg.id == reaction.message.id and str(reaction.emoji) in emjs
    try: reaction, user = await client.wait_for('reaction_add', check=check, timeout=20)
    except asyncio.TimeoutError:
        await asyncio.gather(msg.delete(),ctx.send(embed=get_embed('⏰ | 시간이 초과되었습니다!',"", 0xFF0000)))
        return
    else:
        e = str(reaction.emoji)
        if e == emjs[0]:
            firstemj=['📝', '✏️', '🖋️', '🖊️']
            amsg=await client.get_channel(721338195962363915).send(embed=get_embed(firstemj[randint(0,3)]+f" | **{ctx.author} 대신 전해드립니다**",">>> ```"+arg+'```'))
            emjs=['<:Like:723450822951960607>','<:Love:723450843659239474>','<:Wow:723450883324772372>','<:HaHa:723450860264357980>','<:Sad:723450903025156106>','<:Angry:723450923170529321>','<:Care:723495892132298763>']
            for a in emjs: await amsg.add_reaction(a)
            await asyncio.gather(msg.delete(),ctx.send("<a:check:723540353872953366> 당신의 게시글이 노익명으로 올라갔어요!\n게시글 채널을 확인해주세요!"))
        elif e == emjs[1]:
            await asyncio.gather(msg.delete(),ctx.send("전송이 취소되었습니다."))

@client.command(name='eval')
async def _eval(ctx,*,arg):
    if ctx.author.id == 467666650183761920:
        await ctx.send(embed=get_embed("EVAL",f"```{eval(arg)}```"))

@client.command(name='await')
async def _eval(ctx,*,arg):
    if ctx.author.id == 467666650183761920:
        await eval(arg)

@client.command(name='dm공지')
async def _dm_send(ctx,*,arg):
    if ctx.author != ctx.guild.owner: return
    sendeduser=[]
    for s in ctx.guild.members:
        if s.bot == False:
            try:
                await s.send(arg)
                sendeduser.append(f'<a:689877466705297444:700213356078039061>> **{s.name}**님에게 전송 성공')
            except: sendeduser.append(f'<a:689877428142604390:700213356564578315>> **{s.name}**님에게 전송 실패')
    await ctx.channel.send(embed=get_embed("공지 전송 로그","\n".join(sendeduser)))

client.run("")