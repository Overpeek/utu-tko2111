import pickle;
import math;
import inspect;

from calc_result import Result;



# ------------------
# calc_interpreter memory
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
			"e": math.e,
			"i": 0+1j
		};

		self.functions = {
			"sin": lambda memory, x: Result.ok(math.sin(x)),
			"cos": lambda memory, x: Result.ok(math.cos(x)),
			"tan": lambda memory, x: Result.ok(math.tan(x)),
			"round": lambda memory, x: Result.ok(round(x)),
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

	def __str__(self):
		return f"({self.inner})";

class Num:
	def __init__(self, val):
		if val == ".":
			self.val = 0.0;
		else:
			self.val = float(val);
	
	def visit(self, memory: Memory):
		return Result.ok(self.val);

	def __str__(self):
		return f"{self.val}";

class Const:
	def __init__(self, name):
		self.name = name;
	
	def visit(self, memory: Memory):
		const = memory.constants.get(self.name);
		func = None;
		if const == None:
			const = memory.arguments.get(self.name);
		
		if const == None:
			# 0 arg func as a const
			func = memory.functions.get(self.name);
			custom = False;
			if func == None:
				func = memory.custom_functions.get(self.name);
				custom = True;

			if func != None:
				func_argc = func.argc() if custom else (len(inspect.signature(func).parameters) - 1);
				if func_argc == 0:
					return func(memory);
		
		if const == None:
			if func != None:
				return Result.err(f"Error: constant: '{self.name}' not found\nWarning: function: '{self.name}' exists but it cannot be used as a constant");
			
			return Result.err(f"Error: constant: '{self.name}' not found");
		
		return Result.ok(const);

	def __str__(self):
		return f"{self.name}";

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
		func_argc = (func.argc()) if custom else (len(inspect.signature(func).parameters) - 1);
		func_argc = func_argc;
		given_argc = len(args);

		if func_argc != given_argc:
			return Result.err(f"Error: function argument count mismatch for: '{self.func}' got {given_argc} expected {func_argc}");
		
		calc_result = func(memory, *args);
		if calc_result.is_err:
			return calc_result;
		calc_result = calc_result.inner;
		return Result.ok(calc_result);

	def __str__(self):
		return f"{self.func}({','.join([val.__str__() for val in self.csv])})";

class ImplFunc:
	def __init__(self, name, csv, body):
		self.name = name;
		self.csv = csv;
		self.body = body;

	def visit(self, memory: Memory):
		memory.custom_functions[self.name] = self;
		memory.save();
		return Result.ok(f"ok");

	def argc(self):
		return len(self.csv);

	def __call__(self, memory: Memory, *args):
		args = list(args);

		# if len(args) != len(self.csv):
				# return Result.err(f"Error: function argument count mismatch for: '{self.name}' got {len(args)} expected {len(self.csv)}");

		for (arg, name) in zip(args, self.csv):
			memory.arguments[name] = arg;

		calc_result = self.body.visit(memory);
		memory.arguments.clear();

		return calc_result

	def __str__(self):
		return f"fn {self.name}({','.join(self.csv)}) = {self.body}";

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

	def __str__(self):
		return f"({self.op}{self.factor})";

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

	def __str__(self):
		return f"({self.lhs}{self.op}{self.rhs})";