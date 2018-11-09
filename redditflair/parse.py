from bs4 import BeautifulSoup
import urllib.request, re

PRESTIGE = {
    # Bronze 0 - 5
    '0x0250000000000918': 1,
    '0x0250000000000919': 2,
    '0x025000000000091A': 3,
    '0x025000000000091B': 4,
    '0x025000000000091C': 5,
    '0x025000000000091D': 6,
    '0x025000000000091E': 7,
    '0x025000000000091F': 8,
    '0x0250000000000920': 9,
    '0x0250000000000921': 10,
    '0x0250000000000922': 11,
    '0x0250000000000924': 12,
    '0x0250000000000925': 13,
    '0x0250000000000926': 14,
    '0x025000000000094C': 15,
    '0x0250000000000927': 16,
    '0x0250000000000928': 17,
    '0x0250000000000929': 18,
    '0x025000000000092B': 19,
    '0x0250000000000950': 20,
    '0x025000000000092A': 21,
    '0x025000000000092C': 22,
    '0x0250000000000937': 23,
    '0x025000000000093B': 24,
    '0x0250000000000933': 25,
    '0x0250000000000923': 26,
    '0x0250000000000944': 27,
    '0x0250000000000948': 28,
    '0x025000000000093F': 29,
    '0x0250000000000951': 30,
    '0x025000000000092D': 31,
    '0x0250000000000930': 32,
    '0x0250000000000934': 33,
    '0x0250000000000938': 34,
    '0x0250000000000940': 35,
    '0x0250000000000949': 36,
    '0x0250000000000952': 37,
    '0x025000000000094D': 38,
    '0x0250000000000945': 39,
    '0x025000000000093C': 40,
    '0x025000000000092E': 41,
    '0x0250000000000931': 42,
    '0x0250000000000935': 43,
    '0x025000000000093D': 44,
    '0x0250000000000946': 45,
    '0x025000000000094A': 46,
    '0x0250000000000953': 47,
    '0x025000000000094E': 48,
    '0x0250000000000939': 49,
    '0x0250000000000941': 50,
    '0x025000000000092F': 51,
    '0x0250000000000932': 52,
    '0x025000000000093E': 53,
    '0x0250000000000936': 54,
    '0x025000000000093A': 55,
    '0x0250000000000942': 56,
    '0x0250000000000947': 57,
    '0x025000000000094F': 58,
    '0x025000000000094B': 59,
    '0x0250000000000954': 60,
    # Silver 6 - 11
    '0x0250000000000956': 61,
    '0x025000000000095C': 62,
    '0x025000000000095D': 63,
    '0x025000000000095E': 64,
    '0x025000000000095F': 65,
    '0x0250000000000960': 66,
    '0x0250000000000961': 67,
    '0x0250000000000962': 68,
    '0x0250000000000963': 69,
    '0x0250000000000964': 70,
    '0x0250000000000957': 71,
    '0x0250000000000965': 72,
    '0x0250000000000966': 73,
    '0x0250000000000967': 74,
    '0x0250000000000968': 75,
    '0x0250000000000969': 76,
    '0x025000000000096A': 77,
    '0x025000000000096B': 78,
    '0x025000000000096C': 79,
    '0x025000000000096D': 80,
    '0x0250000000000958': 81,
    '0x025000000000096E': 82,
    '0x025000000000096F': 83,
    '0x0250000000000970': 84,
    '0x0250000000000971': 85,
    '0x0250000000000972': 86,
    '0x0250000000000973': 87,
    '0x0250000000000974': 88,
    '0x0250000000000975': 89,
    '0x0250000000000976': 90,
    '0x0250000000000959': 91,
    '0x0250000000000977': 92,
    '0x0250000000000978': 93,
    '0x0250000000000979': 94,
    '0x025000000000097A': 95,
    '0x025000000000097B': 96,
    '0x025000000000097C': 97,
    '0x025000000000097D': 98,
    '0x025000000000097E': 99,
    '0x025000000000097F': 100,
    '0x025000000000095A': 101,
    '0x0250000000000980': 102,
    '0x0250000000000981': 103,
    '0x0250000000000982': 104,
    '0x0250000000000983': 105,
    '0x0250000000000984': 106,
    '0x0250000000000985': 107,
    '0x0250000000000986': 108,
    '0x0250000000000987': 109,
    '0x0250000000000988': 110,
    '0x025000000000095B': 111,
    '0x0250000000000989': 112,
    '0x025000000000098A': 113,
    '0x025000000000098B': 114,
    '0x025000000000098C': 115,
    '0x025000000000098D': 116,
    '0x025000000000098E': 117,
    '0x025000000000098F': 118,
    '0x0250000000000991': 119,
    '0x0250000000000990': 120,
    # Gold 12 - 17
    '0x0250000000000992': 121,
    '0x0250000000000993': 122,
    '0x0250000000000994': 123,
    '0x0250000000000995': 124,
    '0x0250000000000996': 125,
    '0x0250000000000997': 126,
    '0x0250000000000998': 127,
    '0x0250000000000999': 128,
    '0x025000000000099A': 129,
    '0x025000000000099B': 130,
    '0x025000000000099C': 131,
    '0x025000000000099D': 132,
    '0x025000000000099E': 133,
    '0x025000000000099F': 134,
    '0x02500000000009A0': 135,
    '0x02500000000009A1': 136,
    '0x02500000000009A2': 137,
    '0x02500000000009A3': 138,
    '0x02500000000009A4': 139,
    '0x02500000000009A5': 140,
    '0x02500000000009A6': 141,
    '0x02500000000009A7': 142,
    '0x02500000000009A8': 143,
    '0x02500000000009A9': 144,
    '0x02500000000009AA': 145,
    '0x02500000000009AB': 146,
    '0x02500000000009AC': 147,
    '0x02500000000009AD': 148,
    '0x02500000000009AE': 149,
    '0x02500000000009AF': 150,
    '0x02500000000009B0': 151,
    '0x02500000000009B1': 152,
    '0x02500000000009B2': 153,
    '0x02500000000009B3': 154,
    '0x02500000000009B4': 155,
    '0x02500000000009B5': 156,
    '0x02500000000009B6': 157,
    '0x02500000000009B7': 158,
    '0x02500000000009B8': 159,
    '0x02500000000009B9': 160,
    '0x02500000000009BA': 161,
    '0x02500000000009BB': 162,
    '0x02500000000009BC': 163,
    '0x02500000000009BD': 164,
    '0x02500000000009BE': 165,
    '0x02500000000009BF': 166,
    '0x02500000000009C0': 167,
    '0x02500000000009C1': 168,
    '0x02500000000009C2': 169,
    '0x02500000000009C3': 170,
    '0x02500000000009C4': 171,
    '0x02500000000009C5': 172,
    '0x02500000000009C6': 173,
    '0x02500000000009C7': 174,
    '0x02500000000009C8': 175,
    '0x02500000000009C9': 176,
    '0x02500000000009CA': 177,
    '0x02500000000009CB': 178,
    '0x02500000000009CC': 179,
    '0x02500000000009CD': 180
}

REGIONS = [
	'eu',
	'us',
	'kr'
]

def parseOWProfile(battletag, blizzardid, xblname, psnname, platform):
	if platform == 'pc':
		return parsePCProfile(battletag)
	else:
		return parseConsoleProfile(blizzardid, xblname, psnname, platform)
	
def parseConsoleProfile(blizzardid, xblname, psnname, platform):
	if platform == 'psn':
		psnname = urllib.parse.quote(psnname.replace('#','-'))
		consoleurl = 'https://playoverwatch.com/en-us/career/psn/' + psnname
	else:
		xblname = urllib.parse.quote(xblname.replace('#','-'))
		consoleurl = 'https://playoverwatch.com/en-us/career/xbl/' + xblname

	print(consoleurl)
		
	try:
		html = urllib.request.urlopen(consoleurl)
	except urllib.error.HTTPError as e:
		return None
		
	print(consoleurl)
	
	soup = BeautifulSoup(html, 'html.parser')	
		
	scripts = soup.findAll('script')
	if not scripts:
		return None
	lastscript = scripts[-1]
	foundId = re.match('window.app.career.init\((\d+),', lastscript.get_text(strip=True)).group(1)
		
	if int(foundId) != int(blizzardid):
		return None
		
	# get rank
	rankNode = soup.select('div.competitive-rank')
	rank = 0
	if len(rankNode) > 0:
		rank = rankNode[0].get_text(strip=True)
		
	# get level
	levelNode = soup.select('div.player-level')
	level = 0
	if len(levelNode) > 0:
		levelcode = levelNode[0]['style'].replace('background-image:url(https://d1u1mce87gyfbn.cloudfront.net/game/playerlevelrewards/','').replace('_Border.png)','')
		level = PRESTIGE[levelcode]
		
	if rank == 0:
		rank = None
	return rank
	
def parsePCProfile(battletag):
	battletag = urllib.parse.quote(battletag.replace('#','-'))
	pcurl = 'https://playoverwatch.com/en-us/career/pc/{0}/' + battletag
	
	rank = 0
	level = 0
	
	for region in REGIONS:
		try:
			html = urllib.request.urlopen(pcurl.format(region))
		except urllib.error.HTTPError as e:
			continue
			
		soup = BeautifulSoup(html, 'html.parser')
		
		# get rank
		rankNode = soup.select('div.competitive-rank')
		tempRank = 0
		if len(rankNode) > 0:
			tempRank = rankNode[0].get_text(strip=True)
		else:
			continue
			
		# get level
		#levelNode = soup.select('div.player-level')
		#tempLevel = 0
		#if len(levelNode) > 0:
		#	levelcode = levelNode[0]['style'].replace('background-image:url(https://d1u1mce87gyfbn.cloudfront.net/game/playerlevelrewards/','').replace('_Border.png)','')
		#	tempLevel = PRESTIGE[levelcode]
		
		#if int(tempRank) > int(rank):
		#	rank = tempRank
	
	if rank == 0:
		rank = None
	return rank
