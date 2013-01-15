import argparse
import socket
import sys
from pbot import parse_getaction
from pbot import pbots_calc


class Player:
	def run(self, input_socket):
		# Get a file-object for reading packets from the socket.
		# Using this ensures that you get exactly one packet per read.
		f_in = input_socket.makefile()
		
		myhand = ''
		
		while True:
			# Block until the engine sends us a packet.
			data = f_in.readline().strip()
			# If data is None, connection has closed.
			if not data:
				print "Gameover, engine disconnected."
				break

			# Here is where you should implement code to parse the packets from
			# the engine and act on it. We are just printing it instead.
			#print data
			
			dataSplit = data.split()

			# When appropriate, reply to the engine with a legal action.
			# The engine will ignore all spurious responses.
			# The engine will also check/fold for you if you return an
			# illegal action.
			# When sending responses, terminate each response with a newline
			# character (\n) or your bot will hang!
			word = dataSplit[0]
			if word == "GETACTION":
				parsed_packet = parse_getaction.parse_list(dataSplit)

				if len(parsed_packet['LEGALACTIONS']) == 0:
					# since we only have one legal action, we take it no matter what
					s.send(parsed_packet['LEGALACTIONS'][0] + "\n")
					print "pbot_ took only legal action: " + parsed_packet['LEGALACTIONS'][0]
				else:
					equity = pbots_calc.calc(myhand + ":xxx", ''.join(parsed_packet['BOARDCARDS']), '', 1000).ev[0]
					pot_size = parsed_packet['POTSIZE']
					
					# check how much the opponent raised by, if any
					amountRaised = 0
					canDiscard = False
					
					for action in parsed_packet['LASTACTIONS'][1:]:
						actionSplit = action.split(":")
						
						if actionSplit[0] == "BET" or actionSplit[0] == "RAISE":
							amountRaised += int(actionSplit[1])
					
					# check min/max we can bet/raise by
					betType = "BET"
					minBet = 0
					maxBet = 0
					
					for action in parsed_packet['LEGALACTIONS']:
						actionSplit = action.split(":")
						
						if actionSplit[0] == "BET" or actionSplit[0] == "RAISE":
							if actionSplit[0] == "RAISE":
								betType = "RAISE"
								

							minBet = int(actionSplit[1])
							maxBet = int(actionSplit[2])
						elif actionSplit[0] == "DISCARD":
							canDiscard = True
					
					# print out parameters for this turn
					print "================="
					print "pbot_ my equity: " + str(equity)
					print "pbot_ opponent raised: " + str(amountRaised)
					print "pbot_ pot: " + str(pot_size)
					print "pbot_ bettype: " + betType
					print "pbot_ minbet: " + str(minBet)
					print "pbot_ maxbet: " + str(maxBet)
					print "================="
					
					# based on pot size and equity, determine whether to bet or call or check/fold
					myAction = "CHECK"

					if pot_size < 50:#
						if equity > 0.55:
							# raise up to 5
							mybet = min(maxBet,5)
							myAction = betType + ":" + str(mybet)
						elif equity > 0.45:
							myAction = "CALL"
					elif pot_size < 100:
						if equity > 0.65:
							mybet = pot_size + minBet
							myAction = betType + ":" + str(mybet)
						elif equity > 0.55:
							myAction = "CALL"
					elif pot_size > 100:
						if equity > 0.85:
							mybet = maxBet
							myAction = betType + ":" + str(mybet)
						
						elif equity > 0.65:
							myAction = "CALL"

						elif equity <0.65:
							myAction = "FOLD"
					else:
						if equity > 0.70:
							myAction = "CALL"
					
					if canDiscard:
					
						c1 = myhand[:2]
						c2 = myhand[2:4]
						c3 = myhand[4:]
						hand = c1+c2+c3
						Action = "DISCARD:"
				
						equity_0 = pbots_calc.calc(c2+c3 + ":xxx", ''.join(parsed_packet['BOARDCARDS']), '', 1000).ev[0]
						equity_1 = pbots_calc.calc(c1+c3 + ":xxx", ''.join(parsed_packet['BOARDCARDS']), '', 1000).ev[0]
						equity_2 = pbots_calc.calc(c1+c2 + ":xxx", ''.join(parsed_packet['BOARDCARDS']), '', 1000).ev[0]

						if equity_0 >= equity_1 and equity_0 >= equity_2:
							hand = c2+c3
							print ("DISCARD: " + c1)
							Action += c1  
							
						elif equity_1 >= equity_0 and equity_1 >= equity_2:
							hand = c1+c3
							Action += c2
							print ("DISCARD: " + c2)
							
						elif equity_2 >= equity_0 and equity_2 >= equity_1:
							hand = c1+c2
							Action += c3
						 	print ("DISCARD: " + c3)
						s.send(Action + "\n")

					print "decided to: " + myAction
					s.send(myAction + "\n")
					

					

			elif word == "NEWHAND":
				myhand = dataSplit[3] + dataSplit[4] + dataSplit[5]
				print "pbot_ got new hand: " + myhand

				

			elif word == "REQUESTKEYVALUES":
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

	# Create a socket connection to the engine.
	print 'Connecting to %s:%d' % (args.host, args.port)
	try:
		s = socket.create_connection((args.host, args.port))
	except socket.error as e:
		print 'Error connecting! Aborting'
		exit()

	bot = Player()
	bot.run(s)