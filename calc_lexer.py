TOKEN_EOF = 0;
TOKEN_NUM = 1;
TOKEN_GROUP = 2;
TOKEN_OP = 3;
TOKEN_IDENT = 4;
TOKEN_COMMA = 5;
TOKEN_EQ = 6;

def lex(debug_mode: bool, text: str):
	tokens = [];

	building_num = False;
	num = "";

	building_ident = False;
	ident = "";

	for c in text:
		# if debug_mode:
			# print(f"Debug: lexing: {c}. Building num: {building_num}. Building ident: {building_ident}");

		# num calc_lexer
		if not building_ident and (c.isdigit() or c == '.'):
			building_num = True;
			num += c;
			continue;
		elif building_num:
			tokens.append((TOKEN_NUM, num));
			building_num = False;
			num = "";

		# ident calc_lexer
		if c.isalnum():
			building_ident = True;
			ident += c;
			continue;
		elif building_ident:
			tokens.append((TOKEN_IDENT, ident));
			building_ident = False;
			ident = "";
		
		# group calc_lexer
		if c in '()':
			tokens.append((TOKEN_GROUP, c));
		
		# op calc_lexer
		elif c in '+-*/^':
			tokens.append((TOKEN_OP, c));

		# comma calc_lexer
		elif c == ',':
			tokens.append((TOKEN_COMMA, c));

		# eq calc_lexer
		elif c == '=':
			tokens.append((TOKEN_EQ, c));

	if building_num:
		tokens.append((TOKEN_NUM, num));
	if building_ident:
		tokens.append((TOKEN_IDENT, ident));
		
	tokens.append((TOKEN_EOF, None));
	return tokens;