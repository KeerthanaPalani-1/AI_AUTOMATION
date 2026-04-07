from langchain.messages import AnyMessage
from typing_extensions import TypedDict, Annotated
import operator

#Graph state
class AgentState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int

    csv_file_path: str
    csv_rows: list[dict]
    row_index: int

    validation_errors: list[str]
    validation_result: str

    fixed_document: str

    evaluation_status: str

    human_verification_required: bool
    human_approved: bool

    email_status: str

    current_step: str

    retry_count: int