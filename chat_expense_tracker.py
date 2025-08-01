import os
import json
import datetime
import re
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms import Ollama
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from telegram import InputFile

# === LLM Setup ===
llm = Ollama(model="llama3")

amount_prompt = ChatPromptTemplate.from_template(
    """
    You are a strict JSON extractor.

    Given this text: '{text}', extract all expenses and numeric amounts.

    Return ONLY valid JSON in this format:
    [
      {{"description": "...", "amount": ...}},
      {{"description": "...", "amount": ...}}
    ]

    Rules:
    - Return nothing but valid JSON.
    - Do not include currency names, symbols, or extra text.
    - No markdown.
    """
)

llm_chain = LLMChain(llm=llm, prompt=amount_prompt)

# === Load categories once ===
with open("categories.json", "r") as f:
    CATEGORY_KEYWORDS = json.load(f)

# === Categorization ===
def categorize_expense(description):
    desc = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(word in desc for word in keywords):
            return category
    return "Other"
    

#save expense to excel

def save_expense_to_excel(description, amount):
    date = datetime.date.today()
    month = date.strftime("%Y-%m")
    filename = f"expenses_{month}.xlsx"
    category=categorize_expense(description)

    if os.path.exists(filename):
        workbook = load_workbook(filename)
        sheet = workbook.active
    else:
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(["Date", "Description", "Amount", "Category"])  # header

    sheet.append([str(date), description, amount, category])
    workbook.save(filename)
 
# Download expense sheet
    
async def download_expense_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    month = datetime.date.today().strftime("%Y-%m")
    filename = f"expenses_{month}.xlsx"
    if os.path.exists(filename):
        with open(filename,"rb") as file:
            await update.message.reply_document(InputFile(file, filename=filename))
    else:
        await update.message.reply_text("No expenses recorded yet this month.")

# === Telegram Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hi! Send me your expense in plain text and I’ll categorize and log it for you.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    try:
        response = llm_chain.invoke({"text": user_input})
        print("🔎 Raw LLM Response:", response)

        # Get response text
        response_text = response.get("text") if isinstance(response, dict) else getattr(response, "content", "")

        # Extract valid JSON array from response
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if not json_match:
            raise ValueError("No valid JSON array found in LLM response")

        expenses_json = json_match.group(0)
        expenses = json.loads(expenses_json)

        if not isinstance(expenses, list):
            raise ValueError("Parsed response is not a list")

        confirmation = ""
        for exp in expenses:
            description = exp["description"]
            amount = float(exp["amount"])
            save_expense_to_excel(description, amount)
            confirmation += f"✅ {description}: ₹{amount}\n"

        await update.message.reply_text("Expenses recorded:\n" + confirmation)

    except Exception as e:
        print("❌ Error:", str(e))
        await update.message.reply_text("❌ I couldn't detect valid expenses. Please try again with a clearer format.")
# === Run the Bot ===
if __name__ == "__main__":
    TELEGRAM_BOT_TOKEN = "8334346659:AAEJUNXE1kWxwQDt1VVAyNuC7GwSKAxsT5o"

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("download", download_expense_excel))

    print("🚀 Bot is running...")
    app.run_polling()
