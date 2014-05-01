"""
Puja bot

say <botname>: <anything>
bot says : <foo> : i am a log bot.

Run :
	$python Pujabot.py test test.log

on an IRC channel :
	$python Pujabot.py <channel> <file>

"""
from twisted.words.protocols import IRC
from twisted.internet import reactor, protocol
from twisted.python import log

import time, sys

class MessageLogger:
	"""
	an independent logger class 
	"""
	def _init_(self, file):
		self.file = file

	def log(self, message):
		timestamp = time.strftime("(%H:%M:%S)", time.localtime(time.time()))
		self.file.write('%s %s\n' %(timestamp, message))
		self.file.flush()

	def close(self):
		self.file.close()

class LogBot(irc.IRCClient):
	"""a logging IRC Bot"""
	
	nickname = "PujaBot"

	def connectionMade(self):
		irc.IRCClient.connectionMade(self)
		self.logger = MessageLogger(open(self.factory.filename, "a"))
		self.logger.log("[connected at %s]" % time.asctime(time.localtime(time.time())))


	def connectionLost(self, reason):
		irc.IRCClient.connectionLost(self, reason)
		self.logger.log("[disconnected at %s]" %
			time.asctime(time.localtime(time.time())))
		self.logger.close()

	def signedOn(self):
		self.join(self.factory.channel)

	def joined(self, channel):
		self.logger.log("(I have joined %s)" % channel)

	#def privmsg(self, user, channel, msg):
	#	"""This will get called when the bot receives a message."""
	#	user = user.split(’!’, 1)[0]
	#	self.logger.log("<%s> %s" % (user, msg))
		
		# Check to see if they’re sending me a private message
	#	if channel == self.nickname:
	#		msg = "It isn’t nice to whisper! Play nice with the group."
	#		self.msg(user, msg)

	#	return

	def action(self, user, channel, msg):
		"""This will get called when the bot sees someone do an action."""
		user = user.split(’!’, 1)[0]
		self.logger.log("* %s %s" % (user, msg))

	def irc_NICK():
		old_nick = prefix.split(’!’)[0]
		new_nick = params[0]
		self.logger.log("%s is now known as %s" % (old_nick, new_nick))

	def alterCollidedNick(self, nickname):
			"""
			Generate an altered version of a nickname that caused a collision in an
			effort to create an unused related name for subsequent registration.
			"""
		return nickname + ’ˆ’



class LogBotFactory(protocol.ClientFactory):
	"""A factory for LogBots.
	A new protocol instance will be created each time we connect to the server.
	"""
	def __init__(self, channel, filename):
		self.channel = channel
		self.filename = filename

	def buildProtocol(self, addr):
		p = LogBot()
		p.factory = self
		return p

	def clientConnectionLost(self, connector, reason):
		"""If we get disconnected, reconnect to server."""
		connector.connect()

	def clientConnectionFailed(self, connector, reason):
		print "connection failed:", reason
		reactor.stop()

if __name__ == ’__main__’:
	# initialize logging
	log.startLogging(sys.stdout)
	# create factory protocol and application
	f = LogBotFactory(sys.argv[1], sys.argv[2])
	# connect factory to this host and port
	reactor.connectTCP("irc.freenode.net", 6667, f)
	# run bot
	reactor.run()
