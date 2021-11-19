#!/usr/bin/python3

import sys;

import lexer;
import parser;
from interpreter import Memory;



def run(debug_mode: bool, text: str):
	tokens = lexer.lex(debug_mode, text);
	if debug_mode:
		print(f"Debug: lexer returned: '{tokens}'");
	
	ast = parser.parse(debug_mode, tokens);
	if ast.is_err:
		print(f"Parse error: {ast.inner}");
		return True;
	ast = ast.inner;
	if debug_mode:
		print(f"Debug: parser returned: '{ast}'");
	
	result = ast.visit(Memory());
	if result.is_err:
		print(f"Interpreter error: {result.inner}");
		return True;
	result = result.inner;
	print(f"{result}");
	
	return True;

def commandline(debug_mode: bool):
	try:
		line = input("> ");
	except KeyboardInterrupt:
		# handle <ctrl+c>
		return False;
	if line == "q":
		# handle <q>
		return False;

	return run(debug_mode, line);

if __name__ == "__main__":
	debug_mode = False;
	# parse cli args
	for arg in sys.argv:
		if arg.startswith("-"):
			args = arg.split("-", 1)[1];

			for c in args:
				if c == 'd':
					debug_mode = True;

	while commandline(debug_mode):
		pass