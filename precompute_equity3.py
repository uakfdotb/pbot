from pbot import parse_getaction
from pbot import pbots_calc

suits = ['h', 's', 'd', 'c']
numbers = ['2', '3', '4', '5', '6', '7', '8', '9', 't', 'j', 'q', 'k', 'a']
cards = []

for i in range(4):
	for j in range(13):
		cards.append(numbers[j] + suits[i])

for c1 in range(52):
	for c2 in range(51 - c1):
		c2 += c1 + 1
		for c3 in range(50 - c2):
			c3 += c2 + 1
			hand = cards[c1] + cards[c2] + cards[c3]
			equity = pbots_calc.calc(hand + ":xxx", '', '', 10000).ev[0]
			print hand + "=" + str(equity)
