import os, gspread
from oauth2client.service_account import ServiceAccountCredentials
from services.rag_engine import answer_query
from langchain_google_genai import ChatGoogleGenerativeAI

SHEET_NAME = os.getenv("SHEET_NAME")
CRED_PATH = os.getenv("GOOGLE_SHEETS_CREDENTIALS")

# Authenticate Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CRED_PATH, scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# Categorize tickets using LLM
def categorize_ticket(ticket_content: str) -> str:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
    prompt = f"Classify this support ticket into categories: product_maintenance, billing, warranty, general:\n\n{ticket_content}"
    result = llm.invoke(prompt)
    return result.content.strip()

def create_ticket(ticket_content: str, ticket_by: str):
    category = categorize_ticket(ticket_content)
    solution = answer_query(ticket_content)

    sheet.append_row([ticket_content, category, ticket_by, "OPEN", solution])
    return {
        "ticket_content": ticket_content,
        "ticket_category": category,
        "ticket_by": ticket_by,
        "ticket_status": "OPEN",
        "ticket_solution": solution
    }

def update_ticket_status(ticket_id: int, status: str):
    sheet.update_cell(ticket_id + 1, 5, status)  # Assuming status column is 5
    return {"ticket_id": ticket_id, "status": status}