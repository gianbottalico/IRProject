def mergeDicts(a, b):
	return dict(list(a.items()) + list(b.items()))
def logMessage(reason, message):
	if message[0] == " ":
		print(("  $ " + reason + ": ").ljust(12) + message)

class BgColors:
	header = '\033[95m'
	okblue = '\033[94m'
	okgreen = '\033[92m'
	warning = '\033[93m'
	fail = '\033[91m'
	endc = '\033[0m'

	def disable(self):
		self.header = ''
		self.okblue = ''
		self.okgreen = ''
		self.warning = ''
		self.fail = ''
		self.endc = ''

bgc = BgColors()