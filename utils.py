
SPECIAL_SYMBOLS_LIST = '\'!@#$%^&*-+?_=,<>/".'

def remove_sp_symbols(string):
	res = []
	for char in string:
		if (char.isalnum() or char == ' ') and char not in SPECIAL_SYMBOLS_LIST:
			res.append(char)

	return ''.join(res)

def replace_sp_symbols(string, instead=' '):
	for symbol in SPECIAL_SYMBOLS_LIST:
		string = string.replace(symbol, instead)

	return string

def remove_multiplying_symbols(string, symbol=' '):
	return symbol.join(string.split(symbol))