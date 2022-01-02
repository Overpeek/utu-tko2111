# -----------------
# Rust style Result
# -----------------

class Result:
	def __init__(self, is_ok: bool, inner):
		if isinstance(inner, Result):
			raise TypeError("Result inside of a Result");
		
		self.is_ok = is_ok;
		self.is_err = not is_ok;
		self.inner = inner;

	def ok(inner):
		return Result(True, inner);

	def err(inner):
		return Result(False, inner);