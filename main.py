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

def print_help():
	print(f"Usage:");
	print(f"python main.py [option(s)]");
	print(f"./main.py [option(s)]");
	print(f"options:");
	print(f"\t-c [line]");
	print(f"\t\tRun line directly");
	print(f"\t-h");
	print(f"\t\tView this help page");
	print(f"\t-d");
	print(f"\t\tEnable debug mode");

if __name__ == "__main__":
	debug_mode = False;
	cli_mode = True;
	direct = None;

	expect = [];

	# parse cli args
	for arg in sys.argv:
		if len(expect) != 0:
			n = expect.pop(0);
			if n == 'c':
				direct = arg.strip('"');
			else:
				raise ValueError(f"Expected value for '{c}'' but there is no handler for it");
		elif arg.startswith("-"):
			args = arg.split("-", 1)[1];

			for c in args:
				if c == 'd':
					debug_mode = True;
				elif c == 'c':
					cli_mode = False;
					expect.append(c);
				elif c == 'h':
					print_help();
					exit(0);
				else:
					print(f"Unknown arg: {c}");
					print_help();
					exit(-1);

	if len(expect) != 0:
		print(f"Expected value for '{expect.pop(0)}'");
		exit(0);

	if cli_mode:
		while commandline(debug_mode):
			pass;
	else:
		run(debug_mode, direct);