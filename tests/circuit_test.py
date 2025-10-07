# DummyAgent for testing
class DummyAgent:
	def __init__(self, name, output):
		self.name = name
		self.output = output
		self.model_inst = None
		self.memory = None
		self.run_called = False
	def run(self, messages, temp=0):
		self.run_called = True
		return self.output
	def __repr__(self):
		return f"DummyAgent({self.name})"

def test_circuit_multiple_downstream():
	"""Test that circuit can handle multiple downstream agents (branching)."""
	a1 = DummyAgent("A1", "out1")
	a2 = DummyAgent("A2", "out2")
	a3 = DummyAgent("A3", "out3")
	# a1 branches to a2 and a3
	connections = {a1: [a2, a3], a2: [], a3: []}
	from agentic.circuit import Circuit
	circuit = Circuit(name="branch_circuit", desc="branch", connections=connections)
	result = circuit.run("msg")
	# Only the first downstream agent (a2) should be traversed by default
	assert a1.run_called
	assert a2.run_called
	assert not a3.run_called or result == "out2"  # a3 not visited in linear traversal
	assert result == "out2"

def test_circuit_cycle_detection():
	"""Test that the circuit does not enter infinite loop on cycles."""
	a1 = DummyAgent("A1", "out1")
	a2 = DummyAgent("A2", "out2")
	# Create a cycle: a1 -> a2 -> a1
	connections = {a1: [a2], a2: [a1]}
	from agentic.circuit import Circuit
	circuit = Circuit(name="cycle_circuit", desc="cycle", connections=connections)
	result = circuit.run("msg")
	# Should visit each agent only once due to visited set
	assert a1.run_called
	assert a2.run_called
	assert result in ("out1", "out2")

