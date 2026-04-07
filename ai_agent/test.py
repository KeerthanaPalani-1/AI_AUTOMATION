from ai_agent.agent import graph
from ai_agent.utils.state import AgentState

# Example CSV rows
csv_rows_sample = [
    {"Customer ID": "DD37Cf93aecA6Dc", "First Name": "Peter", "Last Name": "Jackson"},
    {"Customer ID": "1Ef7b82A4CAAD10", "First Name": "Amber", "Last Name": "Grado"},
    {"Customer ID": "6F94879bDAfE5a6", "First Name": "David", "Last Name": "Berry"}
]

initial_state: AgentState = {
    "messages": [],
    "csv_rows": csv_rows_sample,
    "row_index": 0,
    "validation_result": "",
    "evaluation_status": "",
    "human_verification_required": False,
    "human_approved": False,
    "retry_count": 0,
    "current_step": ""
}

result = graph.invoke(initial_state)

print("Pipeline output for test CSV rows:")
print(result)