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
lastRaised = 0 # keep track of how much we put in so we can find old_pot

def debugPrint(string):
	if DEBUG:
		print string

def getBet(betType, minBet, maxBet, myBet, amountRaised):
	global lastRaised
	
	if betType == "RAISE":
		myBet += amountRaised
	
	actualBet = max(minBet, min(maxBet, myBet))
	
	if actualBet > 0:
		lastRaised = actualBet
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
		myBankRoll = 0
		isButton = False

		totalcall=0
		totalcheck=0
		totalfold=0
		totalraise=0
		totalactions=0
		
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
			if packet['PACKETNAME'] == "NEWGAME":
				oppname=packet['OPPNAME']

			elif packet['PACKETNAME'] == "GETACTION":
				
				if len(packet['LASTACTIONS'])>0:
					for action in packet['LASTACTIONS']:
						if oppname in action:
							totalactions+=1
							if 'CALL' in action:
								totalcall+=1
							elif 'CHECK' in action:
								totalcheck+=1
							elif 'FOLD' in action:
								totalfold+=1
							elif 'RAISE' in action:
								totalraise+=1
								
				#Statistical percentages of opp's actions.
				if totalactions>=0:
					percentcall=float(totalcall)/float(totalactions)
					percentcheck=float(totalcheck)/float(totalactions)
					percentfold=float(totalfold)/float(totalactions)
					percentraise=float(totalraise)/float(totalactions)
				
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
					opponentRaised = False
					
					for action in packet['LASTACTIONS'][1:]:
						actionSplit = action.split(":")
						
						if actionSplit[0] == "BET" or actionSplit[0] == "RAISE":
							amountRaised += int(actionSplit[1])
							
							if actionSplit[0] == "RAISE":
								opponentRaised = True
			
			
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
					
					# let old_pot be the pot size before raise
					old_pot = pot_size - amountRaised
					
					if opponentRaised:
						old_pot += lastRaised
					
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
					debugPrint("pbot_ old pot: " + str(old_pot))
					debugPrint("pbot_ bettype: " + betType)
					debugPrint("pbot_ minbet: " + str(minBet))
					debugPrint("pbot_ maxbet: " + str(maxBet))
					debugPrint("pbot_ isButton: " + str(isButton))
					debugPrint("=================")
					
					# if the amountRaised is low, then override check and call it
					overrideCheck = False
					
					if old_pot > 0 and amountRaised / old_pot < 0.3:
						overrideCheck = True
					
					# based on pot size and equity, determine whether to bet or call or check/fold
					myAction = "CHECK"

					if myBankRoll < -1000:
						if equity > 0.75:
							myAction = getBet(betType, minBet, maxBet, 100, amountRaised)
						elif equity > 0.80:
							myAction = getBet(betType, minBet, maxBet, 150, amountRaised)
						elif equity > 0.90:
							myAction = getBet(betType, minBet, maxBet, maxBet, amountRaised)
						else:
							myAction = "CHECK"

					elif random.random() < 0.1 and equity > 0.2:
						myAction = getBet(betType, minBet, maxBet, maxBet, amountRaised)
					
					else:
						if old_pot < 100:
							if section == 'pre':
								equities = [0.55, 0.33]
							elif section == 'flop':
								equities = [0.57, 0.38]
							elif section == 'turn':
								equities = [0.59, 0.40]
							elif section == 'river':
								equities = [0.6, 0.42]
							
							if equity > equities[0]:
								if section == 'pre' or section == 'flop':
									myAction = getBet(betType, minBet, maxBet, 20, amountRaised)
								else:
									myAction = getBet(betType, minBet, maxBet, 50, amountRaised)
							elif equity > equities[1] or overrideCheck:
								myAction = getBet(betType, minBet, maxBet, 10, amountRaised)
						elif old_pot < 200:
							if section == 'pre':
								equities = [0.68, 0.47]
							elif section == 'flop':
								equities = [0.72, 0.56]
							elif section == 'turn':
								equities = [0.76, 0.61]
							elif section == 'river':
								equities = [0.77, 0.67]
							
							if equity > equities[0] :
								# raise more than the pot
								if random.random() < 0.5:
									myAction = getBet(betType, minBet, maxBet, 100, amountRaised)
								else:
									myAction = getBet(betType, minBet, maxBet, 40, amountRaised)
							elif equity > equities[1] or overrideCheck:
								# raise 5
								myAction = getBet(betType, minBet, maxBet, 5, amountRaised)
						elif old_pot < 320:
							if section == 'pre':
								equities = [0.74, 0.72]
							elif section == 'flop':
								equities = [0.75, 0.69]
							elif section == 'turn':
								equities = [0.80, 0.71]
							elif section == 'river':
								equities = [0.84, 0.75]
							
							if equity > equities[0]:
								if random.random() < 0.5:
									myAction = getBet(betType, minBet, maxBet, maxBet, amountRaised)
								else:
									myAction = getBet(betType, minBet, maxBet, 40, amountRaised)
							elif equity > equities[1] or overrideCheck:
								# raise 20
								myAction = getBet(betType, minBet, maxBet, 30, amountRaised)
						else:
							if (equity > 0.70 or overrideCheck):
								# raise 50
								myAction = getBet(betType, minBet, maxBet, 50, amountRaised)

					debugPrint("decided to: " + myAction)
					s.send(myAction + "\n")
			
			elif packet['PACKETNAME'] == "NEWHAND":
				myhand = ''.join(packet['HAND'])
				discarded = ''
				
				debugPrint("pbot_ got new hand: " + myhand)
				if packet['BUTTON'] == "true":
					isButton = True
				else:
					isButton = False
				
				myBankRoll = packet['MYBANK']

			elif packet['PACKETNAME'] == "REQUESTKEYVALUES":
				# At the end, the engine will allow your bot save key/value pairs.
				# Send FINISH to indicate you're done.
				debugPrint("===========================")
				debugPrint("PERCENTCALL: "+str(percentcall))
                                debugPrint("PERCENTCHECK: "+str(percentcheck))
				debugPrint("PERCENTFOLD: "+str(percentfold))
				debugPrint("PERCENTRAISE: "+str(percentraise))
				debugPrint("===========================")
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
