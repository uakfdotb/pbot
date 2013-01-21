import argparse
import socket
import sys
import threading
import time
import random
from pbot import parse_packets
from pbot import pbots_calc
from pbot import precompute_calc

DEBUG = True

def debugPrint(string):
	if DEBUG:
		print string

def getBet(betType, minBet, maxBet, myBet, amountRaised):
	if betType == "RAISE":
		myBet += amountRaised
	
	actualBet = max(minBet, min(maxBet, myBet))
	
	if actualBet > 0:
		return betType + ":" + str(actualBet)
	else:
		return "CALL"

class Player(threading.Thread):
	input_socket = None
	
	def __init__(self, input_socket):
		super(Player, self).__init__()
		self.input_socket = input_socket
	
	def run(self):
		# Get a file-object for reading packets from the socket.
		# Using this ensures that you get exactly one packet per read.
		f_in = self.input_socket.makefile()
		
		myhand = ''
		discarded = ''
		
		while True:
			# Block until the engine sends us a packet.
			data = f_in.readline().strip()
			# If data is None, connection has closed.
			if not data:
				debugPrint("Gameover, engine disconnected.")
				break

			# Here is where you should implement code to parse the packets from
			# the engine and act on it.
			debugPrint(data)
			packet = parse_packets.master_parse(data)

			# When appropriate, reply to the engine with a legal action.
			# The engine will ignore all spurious responses.
			# The engine will also check/fold for you if you return an
			# illegal action.
			# When sending responses, terminate each response with a newline
			# character (\n) or your bot will hang!
			if packet['PACKETNAME'] == "GETACTION":
				if len(packet['LEGALACTIONS']) == 1:
					# since we only have one legal action, we take it no matter what
					
					if packet['LEGALACTIONS'][0] == "DISCARD":
						c1 = myhand[:2]
						c2 = myhand[2:4]
						c3 = myhand[4:]
						Action = "DISCARD:"
						
						equity_0 = pbots_calc.calc(c2+c3 + ":xx", ''.join(packet['BOARDCARDS']), c1, 2000).ev[0]
						equity_1 = pbots_calc.calc(c1+c3 + ":xx", ''.join(packet['BOARDCARDS']), c2, 2000).ev[0]
						equity_2 = pbots_calc.calc(c1+c2 + ":xx", ''.join(packet['BOARDCARDS']), c3, 2000).ev[0]

						if equity_0 >= equity_1 and equity_0 >= equity_2:
							myhand = c2+c3
							discarded = c1
							debugPrint("DISCARD: " + c1)
							Action += c1  
							
						elif equity_1 >= equity_0 and equity_1 >= equity_2:
							myhand = c1+c3
							discarded = c2
							Action += c2
							debugPrint("DISCARD: " + c2)
							
						elif equity_2 >= equity_0 and equity_2 >= equity_1:
							myhand = c1+c2
							discarded = c3
							Action += c3
						 	debugPrint("DISCARD: " + c3)
						s.send(Action + "\n")
					else:
						s.send(packet['LEGALACTIONS'][0] + "\n")
						debugPrint("pbot_ took only legal action: " + packet['LEGALACTIONS'][0])
				else:
					if packet['BOARDCARDS']:
						equity = pbots_calc.calc(myhand + ":xx", ''.join(packet['BOARDCARDS']), discarded, 2000).ev[0]
					else:
						equity = precompute_calc.calc(myhand)
						debugPrint("precomputed")
					
					pot_size = packet['POTSIZE']
					
					# check how much the opponent raised by, if any
					amountRaised = 0
					
					for action in packet['LASTACTIONS'][1:]:
						actionSplit = action.split(":")
						
						if actionSplit[0] == "BET" or actionSplit[0] == "RAISE":
							amountRaised += int(actionSplit[1])
			
			
					# check min/max we can bet/raise by
					betType = "BET"
					minBet = 0
					maxBet = 0
					
					for action in packet['LEGALACTIONS']:
						actionSplit = action.split(":")
						
						if actionSplit[0] == "BET" or actionSplit[0] == "RAISE":
							if actionSplit[0] == "RAISE":
								betType = "RAISE"
							
							minBet = int(actionSplit[1])
							maxBet = int(actionSplit[2])
					
					# detect pre-flop, flop, turn, river
					section = ''
					
					if len(packet['BOARDCARDS']) == 0:
						section = 'pre'
					elif len(packet['BOARDCARDS']) == 3:
						section = 'flop'
					elif len(packet['BOARDCARDS']) == 4:
						section = 'turn'
					elif len(packet['BOARDCARDS']) == 5:
						section = 'river'
					
					# print out parameters for this turn
					debugPrint("=================")
					debugPrint("pbot_ my equity: " + str(equity))
					debugPrint("pbot_ opponent raised: " + str(amountRaised))
					debugPrint("pbot_ pot: " + str(pot_size))
					debugPrint("pbot_ bettype: " + betType)
					debugPrint("pbot_ minbet: " + str(minBet))
					debugPrint("pbot_ maxbet: " + str(maxBet))
					debugPrint("=================")
					
					# if the amountRaised is low, then override check and call it
					overrideCheck = False
					
					if pot_size > 0 and amountRaised / pot_size < 0.3:
						overrideCheck = True
					
					# based on pot size and equity, determine whether to bet or call or check/fold
					myAction = "CHECK"

					if random.random() < 0.1 and equity > 0.2:
						myAction = getBet(betType, minBet, maxBet, maxBet, amountRaised)
					
					elif haveSB and amountRaised == 0:
						if equity > 0.75:
							myAction = getBet(betType, minBet, maxBet, 60, amountRaised)
						elif equity > 0.65:
							myAction = getBet(betType, minBet, maxBet, 40, amountRaised)
						elif equity > 0.55:
							myAction = getBet(betType, minBet, maxBet, 20, amountRaised)
						elif equity > 0.33:
							myAction = getBet(betType, minBet, maxBet, 10, amountRaised)
 
					elif isButton and amountRaised == 0:
						myAction = getBet(betType, minBet, maxBet, 10, amountRaised)
					
					else:
						if pot_size < 50:
							if section == 'pre':
								equities = [0.38, 0.30]
							elif section == 'flop':
								equities = [0.41, 0.33]
							elif section == 'turn':
								equities = [0.48, 0.33]
							elif section == 'river':
								equities = [0.58, 0.40]
							
							if equity > equities[0]:
								myAction = getBet(betType, minBet, maxBet, 15, amountRaised)
							elif equity > equities[1] or overrideCheck:
								myAction = getBet(betType, minBet, maxBet, 10, amountRaised)
						elif pot_size < 100:
							if section == 'pre':
								equities = [0.48, 0.20]
							elif section == 'flop':
								equities = [0.50, 0.40]
							elif section == 'turn':
								equities = [0.54, 0.45]
							elif section == 'river':
								equities = [0.63, 0.50]
							
							if equity > equities[0] :
								# raise more than the pot
								myAction = getBet(betType, minBet, maxBet, pot_size + 60, amountRaised)
							elif equity > equities[1] or overrideCheck:
								# raise 5
								myAction = getBet(betType, minBet, maxBet, pot_size + 5, amountRaised)
						elif pot_size < 160:
							if section == 'pre':
								equities = [0.49, 0.39]
							elif section == 'flop':
								equities = [0.55, 0.42]
							elif section == 'turn':
								equities = [0.61, 0.48]
							elif section == 'river':
								equities = [0.68, 0.56]
							
							if equity > equities[0]:
								myAction = getBet(betType, minBet, maxBet, maxBet, amountRaised)
							elif equity > equities[1] or overrideCheck:
								# raise 20
								myAction = getBet(betType, minBet, maxBet, (pot_size*.5) + 30, amountRaised)
						else:
							if (equity > 0.56 or overrideCheck):
								# raise 50
								myAction = getBet(betType, minBet, maxBet, 50, amountRaised)

					debugPrint("decided to: " + myAction)
					s.send(myAction + "\n")
			
			elif packet['PACKETNAME'] == "NEWHAND":
				myhand = ''.join(packet['HAND'])
				discarded = ''
				
				debugPrint("pbot_ got new hand: " + myhand)
				if packet['BUTTON']:
					isButton = True
				else:
					isButton = False

			elif packet['PACKETNAME'] == "NEWGAME":
				if packet['BIGBLIND']:
					haveSB  = False
				else:
					haveSB = True
				

			elif packet['PACKETNAME'] == "REQUESTKEYVALUES":
				# At the end, the engine will allow your bot save key/value pairs.
				# Send FINISH to indicate you're done.
				s.send("FINISH\n")
		# Clean up the socket.
		s.close()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='A Pokerbot.', add_help=False, prog='pokerbot')
	parser.add_argument('-h', dest='host', type=str, default='localhost', help='Host to connect to, defaults to localhost')
	parser.add_argument('port', metavar='PORT', type=int, help='Port on host to connect to')
	args = parser.parse_args()
	
	# Do preloading here
	precompute_calc.load()

	# Create a socket connection to the engine.
	debugPrint('Connecting to %s:%d' % (args.host, args.port))
	try:
		s = socket.create_connection((args.host, args.port))
	except socket.error as e:
		debugPrint('Error connecting! Aborting')
		exit()

	bot = Player(s)
	#bot.start()
	bot.run()
	
	#time.sleep(0.005)
	
	# Run bot on next port too for easier testing.
	#print 'Connecting to %s:%d' % (args.host, int(args.port)+1)
	#try:
	#s2 = socket.create_connection((args.host, int(args.port)+1))
	#bot2 = Player(s2)
	#bot2.start()
	#except Exception as e:
		#print 'Error test bot! Aborting'
		#exit()
