from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, END
from ai_agent.utils.evaluator_node import evaluate_fix_node, human_verification_node
from ai_agent.utils.fixing_node import fix_document
from ai_agent.utils.response_node import send_final_document_node
from ai_agent.utils.state import AgentState
from ai_agent.utils.validation_node import validate_document

import os
import csv
from langchain.messages import HumanMessage

# The customer document is loaded as input, and for the current implementation, only the first row is processed to keep the workflow straightforward.
def read_document(state: AgentState) -> dict:
    """
    Read CSV from state (test mode) OR from file (prod mode)
    """

    #  Case 1: Test mode (you passed csv_rows manually)
    if state.get("csv_rows"):
        rows = state["csv_rows"]

    #  Case 2: Production mode (read from file)
    else:
        csv_path = os.getenv("CSV_FILE_PATH")

        if not csv_path:
            raise ValueError("CSV_FILE_PATH environment variable not set")

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

    #   Initialize row index safely
    row_index = state.get("row_index", 0)

    if not rows:
        return {
            "messages": [HumanMessage(content="No data found")],
            "current_step": "document_loaded"
        }

    first_row = rows[row_index]

    return {
        "csv_rows": rows,
        "row_index": row_index,
        "messages": [HumanMessage(content=str(first_row))],
        "current_step": "document_loaded"
    }



# -----------------------------
# Conditional Routing
# -----------------------------
def route_after_evaluation(state: AgentState):
    """
    Decide next step after evaluation:
    - Retry fix (with limit)
    - Human verification fallback
    - Send if valid
    """

    retry_count = state.get("retry_count", 0)

    # stop infinite loop → go to human after 3 retries
    if retry_count > 3:
        return "human_verification"

    if state.get("human_verification_required"):
        return "human_verification"

    elif state.get("evaluation_status") != "VALID":
        return "fix_document"

    return "send_document"


def route_after_human_verification(state: AgentState):
    """
    Decide next step after Human-in-the-loop(HITL):
    - Send if approved
    - End if rejected
    """
    if state.get("human_approved"):
        return "send_document"
    return END


# -----------------------------
# Build Graph
# -----------------------------
graph_builder = StateGraph(AgentState)

graph_builder.add_node("read_document", read_document)
graph_builder.add_node("validate_document", validate_document)
graph_builder.add_node("fix_document", fix_document)
graph_builder.add_node("evaluate_fix", evaluate_fix_node)
graph_builder.add_node("human_verification", human_verification_node)
graph_builder.add_node("send_document", send_final_document_node)

# -----------------------------
# Flow
# -----------------------------
graph_builder.set_entry_point("read_document")

# Core pipeline
graph_builder.add_edge("read_document", "validate_document")
graph_builder.add_edge("validate_document", "fix_document")
graph_builder.add_edge("fix_document", "evaluate_fix")

# Conditional edges
graph_builder.add_conditional_edges(
    "evaluate_fix",
    route_after_evaluation,
    {
        "human_verification": "human_verification",
        "fix_document": "fix_document",
        "send_document": "send_document"
    }
)

graph_builder.add_conditional_edges(
    "human_verification",
    route_after_human_verification,
    {
        "send_document": "send_document",
        END: END
    }
)


# -----------------------------
# Compile
# -----------------------------
graph = graph_builder.compile()
print("[DEBUG] Graph compiled successfully.")