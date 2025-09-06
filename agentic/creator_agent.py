sample = """
circuit:
  name: example_circuit
  description: A circuit of multiple agents for a composite workflow

agents:
  - name: react_agent
    type: ReactAgent
    description: Handles reasoning and tool use
    tools: [run_python, run_shell]
  - name: search_agent
    type: BaseAgent
    description: Handles web search queries
    tools: [search_web]
  - name: db_agent
    type: BaseAgent
    description: Handles database queries
    tools: [query_db]

tools:
  - name: run_python
    module: agentic.tools.code_runner
    function: run_python
    description: Executes Python code snippets
  - name: run_shell
    module: agentic.tools.code_runner
    function: run_shell
    description: Executes shell commands
  - name: search_web
    module: agentic.tools.searcher
    function: search_web
    description: Searches the web
  - name: query_db
    module: agentic.tools.db_connector
    function: query_db
    description: Queries the database

connections:
  - from: react_agent
    output: result
    to: search_agent
    input: query
  - from: search_agent
    output: result
    to: db_agent
    input: query
  - from: db_agent
    output: result
    to: final_output
"""

class CreatorAgent:
    



