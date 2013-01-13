# the precomputed equity data
precompute_data = {}

# suits and cards
suits = ['h', 's', 'd', 'c']
numbers = ['2', '3', '4', '5', '6', '7', '8', '9', 't', 'j', 'q', 'k', 'a']
cards = []

def load():
	# generate all the possible cards
	for i in range(4):
		for j in range(13):
			cards.append(numbers[j] + suits[i])
	
	# read from the text files, and load into the precompute_data dictionary
	filenames = ["precompute2.txt", "precompute3.txt"]
	
	for filename in filenames:
		f = open('dat/' + filename, 'r')
		
		for line in f:
			lineSplit = line.split("=")
			precompute_data[hashHand(lineSplit[0])] = float(lineSplit[1])

def calc(hand):
	# calculate equity based on the precompute_data dictionary
	# if we can't find the equity, we throw an exception
	hand = hand.lower()
	
	if hashHand(hand) in precompute_data:
		return precompute_data[hashHand(hand)]
	else:
		raise Exception('Requested hand ' + hand + ' is not precomputed!')

def hashHand(hand):
	# parse every card and multiply by the index in the hand
	# since order doesn't matter, we also sort from lowest index to highest index
	hand = hand.lower()
	card_array = []
	
	for i in range(len(hand) / 2):
		card_array.append(hashCard(hand[i*2:i*2+2]))
	
	card_array.sort()
	
	h = 0 # the total hash
	multiplier = 1 # the current multiplier
	
	for x in card_array:
		h += multiplier * x
		multiplier *= 52
	
	return h

def hashCard(card):
	return cards.index(card)
