import lexer;
import main;
from result import *;
from interpreter import *;



def parse(debug_mode: bool, tokens: []):
	return parse_stmt(debug_mode, tokens);

# -------
# parsers
# -------

def parse_factor(tokens: []):
	(token_type, token) = tokens.pop(0);

	if token_type == lexer.TOKEN_OP:
		# parse unary op
		factor = parse_factor(tokens);
		if factor.is_err:
			return factor;
		factor = factor.inner;
		return Result.ok(Factor(UnaryOp(token, factor)));
	elif token_type == lexer.TOKEN_NUM:
		# parse num
		return Result.ok(Factor(Num(token)));
	elif token_type == lexer.TOKEN_GROUP and token == '(':
		# parse (expr)
		tokens.insert(0, (token_type, token));
		return parse_factor_paren(tokens);
	elif token_type == lexer.TOKEN_IDENT:
		# parse function or a const
		(paren_token_type, paren_token) = tokens[0];
		if paren_token_type == lexer.TOKEN_GROUP and paren_token == '(':
			# parse function call
			csv = parse_csv_expr(tokens);
			if csv.is_err:
				return csv;
			csv = csv.inner;

			return Result.ok(Func(token, csv));
		else:
			# parse const
			return Result.ok(Const(token));

	elif token_type == lexer.TOKEN_EOF:
		return Result.err(f"Unexpected EOF");
	else:
		return Result.err(f"Expected '(', '<num>', '-' or '+'");

def parse_factor_paren(tokens: []):
	(token_type, token) = tokens.pop(0);
	# group begins with '('
	if token_type != lexer.TOKEN_GROUP or token != '(':
		return Result.ok(f"Expected '('");
	
	expr = parse_expr(tokens);
	if expr.is_err:
		return expr;
	expr = expr.inner;

	# group ends with ')'
	(end_group_token_type, end_group_token) = tokens.pop(0);
	if end_group_token_type == lexer.TOKEN_GROUP and end_group_token == ')':
		return Result.ok(expr);
	else:
		return Result.err(f"Expected ')'");

def parse_csv(tokens: [], val):
	csv = [];

	(token_type, token) = tokens.pop(0);
	# group begins with '('
	if token_type != lexer.TOKEN_GROUP or token != '(':
		return Result.ok(f"Expected '('");
	
	# empty csv
	if is_end_paren(*tokens[0]):
		tokens.pop(0);
		return Result.ok(csv);

	while True:
		value = val(tokens);
		if value.is_err:
			return value;
		csv.append(value.inner);

		if is_comma(*tokens[0]):
			tokens.pop(0);
			continue;
		elif is_end_paren(*tokens[0]):
			tokens.pop(0);
			return Result.ok(csv);
		else:
			return Result.err(f"Expected ')' or ','");

def parse_csv_expr(tokens: []):
	return parse_csv(tokens, lambda tokens: parse_expr(tokens));

def parse_csv_ident(tokens: []):
	return parse_csv(tokens, lambda tokens: parse_ident(tokens));

def parse_ident(tokens: []):
	(token_type, token) = tokens.pop(0);
	if token_type == lexer.TOKEN_IDENT:
		return Result.ok(token);
	else:
		return Result.err(f"Expected ident");

def parse_infix_list(tokens: [], sides, op_token: str):
	lhs = sides(tokens);
	if lhs.is_err:
		return lhs;
	lhs = lhs.inner;

	l = [lhs];

	while True:
		(token_type, token) = tokens.pop(0);
		if token_type != lexer.TOKEN_OP or not token in op_token:
			tokens.insert(0, (token_type, token));
			break;

		l.append(token);

		rhs = sides(tokens);
		if rhs.is_err:
			return rhs;
		rhs = rhs.inner;

		l.append(rhs);
	
	return Result.ok(l);

def parse_infix_with_list(l: [], rev: bool):
	if rev:
		l.reverse();
	i = 0;
	lhs = l[i];
	while True:
		if len(l) == i + 1:
			break;
		if rev:
			lhs = BinaryOp(l[i + 2], l[i + 1], lhs);
		else:
			lhs = BinaryOp(lhs, l[i + 1], l[i + 2]);
		i += 2;
	
	return Result.ok(lhs);

def parse_infix_left(tokens: [], sides, op_token: str):
	return parse_infix(tokens, sides, op_token, False);

def parse_infix_right(tokens: [], sides, op_token: str):
	return parse_infix(tokens, sides, op_token, True);

def parse_infix(tokens: [], sides, op_token: str, rev: bool):
	l = parse_infix_list(tokens, sides, op_token);
	if l.is_err:
		return l;
	l = l.inner;
	return parse_infix_with_list(l, rev);

def parse_atom(tokens: []):
	return parse_infix_right(tokens, lambda tokens: parse_factor(tokens), '^');

def parse_term(tokens: []):
	return parse_infix_left(tokens, lambda tokens: parse_atom(tokens), '*/');

def parse_expr(tokens: []):
	return parse_infix_left(tokens, lambda tokens: parse_term(tokens), '+-');

def parse_fn_impl(tokens: []):
	_ = tokens.pop(0); # fn keyword

	name = parse_ident(tokens);
	if name.is_err:
		return name;
	name = name.inner;

	csv = parse_csv_ident(tokens);
	if csv.is_err:
		return csv;
	csv = csv.inner;

	if not is_eq(*tokens.pop(0)):
		return Result.err("Expected '='");

	expr = parse_expr(tokens);
	if expr.is_err:
		return expr;
	expr = expr.inner;

	return Result.ok(ImplFunc(name, csv, expr));

def parse_stmt(debug_mode: bool, tokens: []):
	if is_fn_keyword(*tokens[0]):
		return parse_fn_impl(tokens);
	else:
		return parse_expr(tokens);

# -------
# helpers
# -------

def is_end_paren(token_type, token):
	return token_type == lexer.TOKEN_GROUP and token == ')';

def is_comma(token_type, token):
	return token_type == lexer.TOKEN_COMMA;

def is_fn_keyword(token_type, token):
	return token_type == lexer.TOKEN_IDENT and token == "fn";

def is_eq(token_type, token):
	return token_type == lexer.TOKEN_EQ;