from dotenv import load_dotenv
load_dotenv()

import os
import smtplib
from email.mime.text import MIMEText
from fastmcp import FastMCP
from ai_agent.utils.state import AgentState

# Create MCP server
mcp = FastMCP("client_communication")

# Email tool
@mcp.tool()
def send_report_via_email(report: str):
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        sender_email = os.getenv("SENDER_EMAIL")
        receiver_email = os.getenv("RECEIVER_EMAIL")
        app_password = os.getenv("EMAIL_APP_PASSWORD")

        if not all([sender_email, receiver_email, app_password]):
            return "Error: Missing email credentials in environment."

        msg = MIMEText(report)
        msg["Subject"] = "Final Approved Document"
        msg["From"] = sender_email
        msg["To"] = receiver_email

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)

        return "Email sent successfully"

    except Exception as e:
        return f"Failed to send email: {e}"


# Final graph node
def send_final_document_node(state: AgentState) -> dict:
    final_document = state["messages"][-1].content if state.get("messages") else ""
    result = send_report_via_email(final_document)

    return {
        "email_status": result,
        "current_step": "document_sent_to_customer"
    }
