import pickle;
import math;
import inspect;

from result import Result;



# ------------------
# Interpreter memory
# ------------------

save_file = "functions.pickle";

class Memory:
	def save(self):
		with open(save_file, "wb") as file:
			pickle.dump(self.custom_functions, file, protocol=pickle.HIGHEST_PROTOCOL);

	def load(self):
		try:
			with open(save_file, "rb") as file:
				self.custom_functions.update(pickle.load(file));
		except FileNotFoundError:
			pass;

	def __init__(self):
		self.constants = {
			"pi": math.pi,
			"e": math.e
		};

		self.functions = {
			"sin": lambda memory, x: Result.ok(math.sin(x)),
			"cos": lambda memory, x: Result.ok(math.cos(x)),
			"tan": lambda memory, x: Result.ok(math.tan(x)),
		};

		self.custom_functions = {}

		self.arguments = {}

		self.load();

	def __del__(self):
		self.save();

# ---
# AST
# ---

class Factor:
	def __init__(self, inner):
		self.inner = inner;
	
	def visit(self, memory: Memory):
		return self.inner.visit(memory);

class Num:
	def __init__(self, val):
		self.val = float(val);
	
	def visit(self, memory: Memory):
		return Result.ok(self.val);

class Const:
	def __init__(self, name):
		self.name = name;
	
	def visit(self, memory: Memory):
		const = memory.constants.get(self.name);
		if const == None:
			const = memory.arguments.get(self.name);
		if const == None:
			return Result.err(f"Error: constant: '{self.name}' not found");
		
		return Result.ok(const);

class Func:
	def __init__(self, func, csv):
		self.func = func;
		self.csv = csv;
	
	def visit(self, memory: Memory):
		custom = False;

		# find the correct function
		func = memory.functions.get(self.func);
		if func == None:
			func = memory.custom_functions.get(self.func);
			custom = True;
		if func == None:
			return Result.err(f"Error: function: '{self.func}' not found");
		
		# setup args
		args = [];
		for val in self.csv:
			val = val.visit(memory);
			if val.is_err:
				return val;
			args.append(val.inner);
		args = tuple(args);

		# validate argc
		if not custom:
			func_argc = len(inspect.signature(func).parameters) - 1;
			given_argc = len(args);

			if func_argc != given_argc:
				return Result.err(f"Error: function argument count mismatch for: '{self.func}' got {given_argc} expected {func_argc}");
		
		result = func(memory, *args);
		if result.is_err:
			return result;
		result = result.inner;
		return Result.ok(result);

class ImplFunc:
	def __init__(self, name, csv, body):
		self.name = name;
		self.csv = csv;
		self.body = body;

	def visit(self, memory: Memory):
		memory.custom_functions[self.name] = self;
		memory.save();
		return Result.ok(f"ok");

	def __call__(self, memory: Memory, *args):
		for (arg, name) in zip(list(args), self.csv):
			memory.arguments[name] = arg;

		result = self.body.visit(memory);
		memory.arguments.clear();

		return result

class UnaryOp:
	def __init__(self, op, factor):
		self.op = op;
		self.factor = factor;
	
	def visit(self, memory: Memory):
		factor = self.factor.visit(memory);
		if factor.is_err:
			return factor;
		factor = factor.inner;

		if self.op == '-':
			return Result.ok(-factor);
		elif self.op == '+':
			return Result.ok(factor);
		else:
			return Result.err(f"Error: unary op: '{op}' is not supported");

class BinaryOp:
	def __init__(self, lhs, op, rhs):
		self.op = op;
		self.lhs = lhs;
		self.rhs = rhs;
	
	def visit(self, memory: Memory):
		lhs = self.lhs.visit(memory);
		if lhs.is_err:
			return lhs;
		lhs = lhs.inner;

		rhs = self.rhs.visit(memory);
		if rhs.is_err:
			return rhs;
		rhs = rhs.inner;

		if self.op == '-':
			return Result.ok(lhs - rhs);
		elif self.op == '+':
			return Result.ok(lhs + rhs);
		elif self.op == '*':
			return Result.ok(lhs * rhs);
		elif self.op == '/':
			return Result.ok(lhs / rhs);
		elif self.op == '^':
			return Result.ok(lhs ** rhs);
		else:
			return Result.err(f"Error: binary op: '{op}' is not supported");