
def remove_sp_symbols(string):
	special_symbols_list = '\'!@#$%^&*-+?_=,<>/" .'
	res = []
	for char in string:
		if char.isalnum() or char in special_symbols_list:
			res.append(char)

	return ''.join(res)