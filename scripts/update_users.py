import requests
import json
import sqlite3
import praw
import re
from database import Flair, Database, User
from collections import defaultdict

dbConn = sqlite3.connect("cowserver.db")
dbConnOld = sqlite3.connect("cowserver_old.db")
subreddit_read = "CompetitiveOverwatch"
subreddit_write = "CompetitiveOverwatch"


removed = {'1246','ahq-e-sports-club','alter-ego','alter-ego2','ambitious-immortals','anox','ardeont','based-tryhards','bazaar','bermuda','black-dragons','blank-blue','blossom','breakaway','caverna-e-sports','chaos-theory','conbox','copenhagen-flames','cyclops-athlete-gaming','darksided','detonatorkorea','dogma','dose','eclipse','ence-esports','encore-esports','exl-esports','first-gen','flag-ar','flag-at','flag-be','flag-ch','flag-co','flag-il','flag-in','flag-is','flag-ku','flag-kw','flag-lv','flag-mx','flag-my','flag-ph','flag-py','flag-ro','flag-sa','flag-tr','flag-vn','flag-za','flash-lux','flash-wolves','fmc','ftd-club','future-group','gamersorigin','geekstar','ge-pantheon-kr','ggea','giant-esports','giant-lynx','grandxur','grizzlys','hero-taciturn-panther','hong-kong-attitude','hsl','jam-gaming','jigsaw','jupiter','just-w','kanga-esports','kix','kraken','laboratory','laoyinbi','ldlc','legacy-esports','lfo','LFTOWL','lgd-gaming','lge-huya','libalent-supreme','lingan-e-sports','logitechg-a-bang','lucky-future-zenith','luxurywatch-red','lynxth','machi-esports','masterminds-gc','mavericks','mega-thunder','meta-bellum','miracle-team-one','monster-shield-kr','moonlight','mosaic-esports','moss-seven-club','movistar-riders','mvp-space','new-paradigm','nga','nocturnal-predators','nocturns-gaming','nova-esports','oh-my-god','one-of-us','one-point','oneshine-esports','osh-tekk-wariors','pain-gaming','phoenix','piece-of-cake','predators-esports','quad','restart','rox-orcas','rx-foxes','scylla-esports','second-generation ','serenity','seven','simplicity','skadis-gift','squid12324','super-number-1','tainted-minds','team-for-victory','team-laffey','team-singularity','team-stormquake','thats-a-disband','those-guys','triple-six-legend','vici-gaming','waeg','we-have-org','wgs-armament','wgs-laurel-nine','wildcat','winstrike-team','witchhunt','ws-esports','x6-gaming','xten-esports','yoshimoto-encount','zenith-of-optimism'}
remapped = {'intz': 'betrayed', 'btrg': 'big-time-regal-gaming', 'fury': 'dignity', 'heist': 'ground-zero', 'nova-mon-shield': 'mega-esports', 'o2-ardeont': 'o2-blast', 'ow-world-cup-2017-logo': 'ow-world-cup-logo', 'isurus-gaming': 'patitos', 'lowkey': 'team-not-found', 'guangzhou-academy': 'the-one-winner', 't1w': 'the-one-winner', 'chick-cont': 'third-impact', 'chicken-contendies': 'third-impact', 'up': 'up-gaming', 'suquinho': 'war-pigs', 'team-clarity': 'war-pigs', 'blank-esports': 'warriors-esports'}


def clear_users():
	c = dbConn.cursor()
	c.execute('''
		DELETE FROM user
	''')
	dbConn.commit()

	if c.rowcount > 0:
		return True
	else:
		return False


def add_user(user):
	c = dbConn.cursor()
	try:
		c.execute('''
			INSERT INTO user
			(name, flair1, flair2, flairtext, is_mod, special_id, special_text)
			VALUES (?, ?, ?, ?, ?, ?, ?)
		''', (user.name, user.flair1, user.flair2, user.flairtext, user.is_mod, user.special_id, user.special_text))
	except sqlite3.IntegrityError:
		return False

	dbConn.commit()
	return True


def get_user(user_name):
	c = dbConn.cursor()
	result = c.execute('''
		SELECT flair1, flair2, flairtext, is_mod, special_id, special_text
		FROM user
		WHERE name = ?
	''', (user_name,))

	result_tuple = result.fetchone()

	if not result_tuple:
		return None
	else:
		return User(
			name=user_name,
			flair1=result_tuple[0],
			flair2=result_tuple[1],
			flairtext=result_tuple[2],
			is_mod=result_tuple[3],
			special_id=result_tuple[4],
			special_text=result_tuple[5]
		)


def get_flairs():
	c = dbConn.cursor()
	new_flairs = {}
	for row in c.execute('''
			SELECT short_name, name, sheet, category, is_active, col, row, is_dirty
			FROM flair
			'''):
		flair = Flair(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
		new_flairs[flair.short_name] = flair
	return new_flairs


def get_specials():
	c = dbConnOld.cursor()
	specials = {}
	for row in c.execute('''
			SELECT name, specialid, text
			FROM specials
			'''):
		specials[row[0]] = {'special_id': row[1], 'special_text': row[2]}
	return specials


def get_flair(name, flair1, flair2, flairtext, special_id, special_text):
	text = ''
	css_class = ''
	if flair1:
		css_class += 's' + flair1.sheet + '-c' + flair1.col + '-r' + flair1.row
		text += ':' + flair1.short_name + ':'
	if flair2:
		css_class += '-2s' + flair2.sheet + '-2c' + flair2.col + '-2r' + flair2.row
		text += ':' + flair2.short_name + ':'

	# special text
	if special_text:
		# truncate if necessary
		max_len = 64 - len(text) - 3
		special_text = special_text[:max_len] if len(special_text) > max_len else special_text
		text = special_text + u' \u2014 ' + text

	# custom text
	if flairtext:
		# truncate if necessary
		max_len = 64 - len(text) - 3
		if max_len > 0:
			custom_text = flairtext[:max_len] if len(flairtext) > max_len else flairtext
			text = custom_text + u' \u2014 ' + text

	return {'user': name, 'flair_css_class': css_class, 'flair_text': text}
	# set flair via praw
	# subreddit = reddit_praw.subreddit(subreddit_write)
	# subreddit.flair.set(name, css_class=css_class, text=text)


def decode(input):
	if input is None:
		return ""
	return input.encode(encoding='ascii', errors='ignore').decode()


with open("flairs_old.json", 'r') as input_file:
	input_text = input_file.read()
	json_data = json.loads(input_text)

flairs = defaultdict(lambda: defaultdict(lambda: defaultdict(str)))
for key in json_data['flairs']:
	flair_json = json_data['flairs'][key]
	flairs[flair_json['sheet']][flair_json['row']][flair_json['col']] = key

r = praw.Reddit("OWMatchThreads", user_agent="script agent")

processed_users = set()
with open("output.txt", 'r') as input_file:
	for line in input_file.readlines():
		items = line.split("\t")
		processed_users.add(items[0])

print(f"Processed users: {len(processed_users)}")

total_users = 0
for flair in r.subreddit(subreddit_read).flair(limit=None):
	total_users += 1

print(f"Total flairs: {total_users}")

#clear_users()
new_flairs = get_flairs()
specials = get_specials()
output = open('output.txt', 'a')
count = 0
flair_updates = []
for flair in r.subreddit(subreddit_read).flair(limit=None):
	count += 1
	if count % 100 == 0:
		print(f"{count}|{total_users}")

	name = flair['user'].name
	css = flair['flair_css_class']
	text = flair['flair_text']
	if name in processed_users:
		continue

	output.write(f"{name}\t{decode(text)}\t{css}\n")

	user = get_user(name)
	if user is None:
		if not css:
			continue

		flair_text = None
		if text and u'\u2014' in text:
			flair_text = text[:text.find(u'\u2014')].strip()

		flair1 = None
		sheet = None
		row = None
		col = None
		first = re.search(r'^s(\w+)-c(\d\d)-r(\d\d)', css)
		if first and len(first.groups()) == 3:
			sheet = first.group(1)
			row = first.group(3)
			col = first.group(2)
		else:
			first = re.search(r'^s(\w+)-r(\d\d)-c(\d\d)', css)
			if first and len(first.groups()) == 3:
				sheet = first.group(1)
				row = first.group(2)
				col = first.group(3)

		if sheet and sheet in flairs and row in flairs[sheet] and col in flairs[sheet][row]:
			flair1 = flairs[sheet][row][col]

		flair2 = None
		sheet = None
		row = None
		col = None
		second = re.search(r'2s(\w+)-2c(\d\d)-2r(\d\d)$', css)
		if second and len(second.groups()) == 3:
			sheet = second.group(1)
			row = second.group(3)
			col = second.group(2)
		else:
			second = re.search(r'2s(\w+)-2r(\d\d)-2c(\d\d)$', css)
			if second and len(second.groups()) == 3:
				sheet = second.group(1)
				row = second.group(2)
				col = second.group(3)

		if sheet and sheet in flairs and row in flairs[sheet] and col in flairs[sheet][row]:
			flair2 = flairs[sheet][row][col]

		if flair1 in removed:
			flair1 = None
		if flair2 in removed:
			flair2 = None
		if flair1 in remapped:
			flair1 = remapped[flair1]
		if flair2 in remapped:
			flair2 = remapped[flair2]

		flair1_object = None
		if flair1 in new_flairs:
			flair1_object = new_flairs[flair1]
		elif flair1 is not None:
			print(f"Unknown flair: {flair1}")
		flair2_object = None
		if flair2 in new_flairs:
			flair2_object = new_flairs[flair2]
		elif flair2 is not None:
			print(f"Unknown flair: {flair2}")

		user = User(name=name, flair1=flair1, flair2=flair2, flairtext=flair_text)

		if user.name in specials:
			special = specials[user.name]
			if special['special_id'] == 'moderator':
				user.is_mod = True
			else:
				user.special_id = special['special_id']
				user.special_text = special['special_text']

		add_user(user)

	else:
		flair1_object = None
		if user.flair1 in new_flairs:
			flair1_object = new_flairs[user.flair1]
		elif user.flair1 is not None:
			print(f"Unknown flair: {user.flair1}")
		flair2_object = None
		if user.flair2 in new_flairs:
			flair2_object = new_flairs[user.flair2]
		elif user.flair2 is not None:
			print(f"Unknown flair: {user.flair2}")

	flair_updates.append(get_flair(user.name, flair1_object, flair2_object, user.flairtext, user.special_id, user.special_text))


print(f"Flairs to update: {len(flair_updates)}")

r.subreddit(subreddit_write).flair.update(flair_updates)

output.close()
dbConn.close()
dbConnOld.close()

