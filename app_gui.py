"""
FraudGuard AI Assistant

This script initializes a professional, clean GUI for the FraudGuard AI Assistant.
It provides intelligent fraud analysis through natural language interface.

Requirements:
- Python 3.8+
- ttkbootstrap>=1.10.1
- spacy>=3.7.2
- Pillow>=10.0.0
- tabulate>=0.9.0
- pandas>=2.0.0
- transformers>=4.36.0
- torch>=2.1.0
- accelerate>=0.25.0
- en-core-web-md @ https://github.com/explosion/spacy-models/releases/download/en_core_web_md-3.7.1/en_core_web_md-3.7.1-py3-none-any.whl
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from db_utils import establish_connection, run_query
from nlp_utils import detect_intent
from supported_questions import INTENTS
from mistral_utils import MistralHandler
import spacy
from tabulate import tabulate
import pandas as pd
from typing import Optional
import threading
import time
from PIL import Image, ImageTk
import smtplib
from email.message import EmailMessage
import tempfile
import os

# Professional color palette
BG_COLOR = "#ffffff"  # Clean white background
PANEL_COLOR = "#f8f9fa"  # Light gray for panels
ACCENT_COLOR = "#0d6efd"  # Professional blue
TEXT_COLOR = "#212529"  # Dark gray for text
SECONDARY_COLOR = "#6c757d"  # Secondary text color
BORDER_COLOR = "#dee2e6"  # Border color
HOVER_COLOR = "#e9ecef"  # Hover state color
FONT_MAIN = ("Segoe UI", 14, "bold")  # Smaller main font

class NLPBotApp:
    def __init__(self, master):
        self.master = master
        master.title("FraudGuard AI Assistant")
        master.geometry("1400x800")

        # Dynamic background image setup
        self.bg_image_path = r"C:/Users/Zol0/Mini-model-For-BI/v904-nunny-012.jpg"
        self.original_bg = Image.open(self.bg_image_path)
        self.bg_photo = None
        self.bg_image_id = None

        self.canvas = tk.Canvas(master, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Frame for all UI widgets
        self.ui_frame = tk.Frame(self.canvas, bg=BG_COLOR)
        self.canvas_window = self.canvas.create_window(0, 0, anchor="nw", window=self.ui_frame)

        master.bind("<Configure>", self._resize_bg)

        self.nlp = spacy.load("en_core_web_md")
        self.intent_docs = {
            intent: [self.nlp(text) for text in data["examples"]]
            for intent, data in INTENTS.items()
        }

        # Initialize Mistral handler
        self.mistral_handler = MistralHandler()
        self.ai_available = self.mistral_handler.is_available()

        self.server = None
        self.database = None
        self.last_result_df: Optional[pd.DataFrame] = None
        self.loading_frame = None

        self.create_server_db_widgets()

    def _resize_bg(self, event):
        # Resize the background image to fit the window
        if event.widget != self.master:
            return
        w, h = event.width, event.height
        if w < 10 or h < 10:
            return
        resized = self.original_bg.resize((w, h), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(resized)
        if self.bg_image_id is None:
            self.bg_image_id = self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
        else:
            self.canvas.itemconfig(self.bg_image_id, image=self.bg_photo)
        self.canvas.lower(self.bg_image_id)  # Keep background at the back
        # Resize the UI frame window on the canvas
        self.canvas.coords(self.canvas_window, 0, 0)
        self.canvas.itemconfig(self.canvas_window, width=w, height=h)

    def create_server_db_widgets(self):
        for widget in self.ui_frame.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.ui_frame, bg=BG_COLOR)
        frame.pack(expand=True)

        # Title with underscore effect
        title_frame = tk.Frame(frame)
        title_frame.grid(row=0, column=0, columnspan=2, pady=(40, 20))
        
        title = tk.Label(title_frame, text="FraudGuard AI Assistant", 
                        font=("Segoe UI", 24, "bold"),
                        fg=ACCENT_COLOR)
        title.pack()
        
        subtitle = tk.Label(title_frame, text="Intelligent Fraud Analysis & Natural Language Interface", 
                          font=("Segoe UI", 12),
                          fg=SECONDARY_COLOR)
        subtitle.pack(pady=(0, 5))
        
        # Underscore line
        underscore = tk.Frame(title_frame, height=3, bg=ACCENT_COLOR)
        underscore.pack(fill="x", pady=(5, 0))

        tk.Label(frame, text="Server:", font=FONT_MAIN, fg=TEXT_COLOR).grid(row=1, column=0, sticky="e", padx=10, pady=10)
        self.server_entry = tb.Entry(frame, width=30, font=FONT_MAIN)
        self.server_entry.insert(0, "")
        self.server_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(frame, text="Database:", font=FONT_MAIN, fg=TEXT_COLOR).grid(row=2, column=0, sticky="e", padx=10, pady=10)
        self.database_entry = tb.Entry(frame, width=30, font=FONT_MAIN)
        self.database_entry.insert(0, "")
        self.database_entry.grid(row=2, column=1, padx=10, pady=10)

        connect_btn = tb.Button(frame, text="Connect", command=self.try_connect, width=20)
        connect_btn.grid(row=3, column=0, columnspan=2, pady=(20, 40))

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

    def try_connect(self):
        self.server = self.server_entry.get().strip()
        self.database = self.database_entry.get().strip()
        try:
            conn = establish_connection(self.server, self.database)
            conn.close()
            messagebox.showinfo("Connection Status", "✅ Connection established successfully!")
            self.create_widgets()
        except Exception as e:
            messagebox.showerror("Connection Status", f"❌ Failed to connect: {e}")

    def create_widgets(self):
        for widget in self.ui_frame.winfo_children():
            widget.destroy()

        # Create main container with padding
        container = tk.Frame(self.ui_frame, bg=BG_COLOR)
        container.pack(expand=True, fill="both", padx=20, pady=20)

        frame = tk.Frame(container, bg=BG_COLOR)
        frame.pack(expand=True, fill="both")

        # Title with bottom border
        title_frame = tk.Frame(frame)
        title_frame.grid(row=0, column=0, columnspan=3, pady=(20, 30), sticky="ew")
        title = tk.Label(title_frame, text="FraudGuard AI Assistant", font=("Segoe UI", 22, "bold"),
                         fg=ACCENT_COLOR)
        title.pack()
        
        subtitle = tk.Label(title_frame, text="Intelligent Fraud Analysis & Natural Language Interface", 
                          font=("Segoe UI", 12),
                          fg=SECONDARY_COLOR)
        subtitle.pack(pady=(0, 5))
        
        separator = tk.Frame(title_frame, height=2, bg=BORDER_COLOR)
        separator.pack(fill="x", pady=(10, 0))

        # Example questions panel with rounded corners and shadow effect
        example_panel = tk.Frame(frame, bg=PANEL_COLOR, bd=1, relief="solid")
        example_panel.grid(row=1, column=0, padx=(40, 20), pady=20, sticky="ns")
        
        # Header for examples
        header_frame = tk.Frame(example_panel, bg=ACCENT_COLOR)
        header_frame.pack(fill="x")
        tk.Label(
            header_frame,
            text="Example Questions",
            font=FONT_MAIN,
            fg="#ffffff",
            bg=ACCENT_COLOR,
            padx=15,
            pady=10
        ).pack(anchor="w")

        # Example questions with improved styling and bot icon
        example_list = [
            ("Show monthly fraud analysis summary.", "Monthly summary of fraud analysis"),
            ("Get all transaction data.", "Get all table from sql"),
            ("List categories with their total and fraudulent amounts.", "Total categories with Fraud amount")
        ]
        tooltip = None

        for ex, tooltip_text in example_list:
            row = tk.Frame(example_panel, bg=PANEL_COLOR)
            row.pack(anchor="w", padx=15, pady=10, fill="x")
            # Bot icon at the start
            bot_icon = tk.Label(
                row,
                text="🤖",
                font=("Segoe UI", 12),
                fg=ACCENT_COLOR,
                bg=PANEL_COLOR
            )
            bot_icon.pack(side="left", padx=(0, 6))
            label = tk.Label(
                row,
                text=f"{ex}",
                font=("Segoe UI", 12),
                fg=TEXT_COLOR,
                bg=PANEL_COLOR,
                cursor="hand2"
            )
            label.pack(side="left")

            # On click, insert example into question entry
            def on_example_click(event, example_text=ex):
                self.question_entry.delete(0, tk.END)
                self.question_entry.insert(0, example_text)
            label.bind("<Button-1>", on_example_click)

            icon = tk.Label(
                row,
                text="ℹ️",
                font=("Segoe UI", 12),
                fg=ACCENT_COLOR,
                bg=PANEL_COLOR,
                cursor="hand2"
            )
            icon.pack(side="left", padx=(5, 0))

            # Add hover effect (fixed)
            def on_enter_row(event, row=row):
                row.configure(bg=HOVER_COLOR)
                for widget in row.winfo_children():
                    # Only configure bg for widgets that support it (Frame, Label)
                    if isinstance(widget, (tk.Frame, tk.Label)):
                        widget.configure(bg=HOVER_COLOR)

            def on_leave_row(event, row=row):
                row.configure(bg=PANEL_COLOR)
                for widget in row.winfo_children():
                    if isinstance(widget, (tk.Frame, tk.Label)):
                        widget.configure(bg=PANEL_COLOR)

            row.bind("<Enter>", lambda event, row=row: on_enter_row(event, row))
            row.bind("<Leave>", lambda event, row=row: on_leave_row(event, row))
            for widget in row.winfo_children():
                widget.bind("<Enter>", lambda event, row=row: on_enter_row(event, row))
                widget.bind("<Leave>", lambda event, row=row: on_leave_row(event, row))

            # Tooltip logic
            def on_enter(event, tip=tooltip_text):
                nonlocal tooltip
                x = event.widget.winfo_rootx() + 20
                y = event.widget.winfo_rooty() + 20
                tooltip = tk.Toplevel()
                tooltip.wm_overrideredirect(True)
                tooltip.geometry(f"+{x}+{y}")
                tooltip_frame = tk.Frame(tooltip, background=ACCENT_COLOR, bd=1)
                tooltip_frame.pack()
                tk.Label(
                    tooltip_frame,
                    text=tip,
                    background="#ffffff",
                    foreground=TEXT_COLOR,
                    relief="flat",
                    padx=10,
                    pady=5,
                    font=("Segoe UI", 10)
                ).pack()

            def on_leave(event):
                nonlocal tooltip
                if tooltip:
                    tooltip.destroy()
                    tooltip = None

            icon.bind("<Enter>", on_enter)
            icon.bind("<Leave>", on_leave)

        # Main interaction panel with improved styling
        main_panel = tk.Frame(frame)
        main_panel.grid(row=1, column=1, padx=(20, 40), pady=20, sticky="nsew")

        # Remove the duplicate title and just keep the question label
        self.question_label = tk.Label(main_panel, text="Ask your question:", 
                                     font=FONT_MAIN, fg=ACCENT_COLOR)
        self.question_label.pack(anchor="w", pady=(10, 5))

        # Question entry with subtle border
        entry_frame = tk.Frame(main_panel, bg=BORDER_COLOR, bd=1, relief="solid")
        entry_frame.pack(fill="x", padx=10, pady=(0, 20))
        self.question_entry = tb.Entry(entry_frame, width=50, font=("Segoe UI", 14))
        self.question_entry.pack(fill="x", padx=1, pady=1, ipady=8)

        # Button container for better alignment
        button_frame = tk.Frame(main_panel)
        button_frame.pack(pady=(0, 20))
        
        # Styled buttons
        self.ask_button = tb.Button(button_frame, text="Ask", command=self.process_question, 
                                  width=12, style="primary.TButton")
        self.ask_button.pack(side="left", padx=5)

        self.export_button = tb.Button(button_frame, text="Export", command=self.export_results, 
                                     width=12, style="excel.TButton")
        self.export_button.pack(side="left", padx=5)

        self.send_email_button = tb.Button(
            button_frame, text="Send to Email", command=self.send_results_email,
            width=14, style="success.TButton"
        )
        self.send_email_button.pack(side="left", padx=5)

        # Result text area with improved styling
        result_frame = tk.Frame(main_panel, bg=BORDER_COLOR, bd=1, relief="solid")
        result_frame.pack(fill="both", expand=True, padx=10)
        
        self.result_text = tk.Text(result_frame, height=20, width=60, font=("Consolas", 12),
                                 bg=BG_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, 
                                 wrap="word", bd=0, relief="flat")
        self.result_text.pack(fill="both", expand=True, padx=1, pady=1)

        # Add "Powered by" text at the bottom right
        powered_frame = tk.Frame(main_panel)
        powered_frame.pack(fill="x", pady=(5, 0))
        
        powered_label = tk.Label(
            powered_frame,
            text="Powered by Microsoft Phi-2",
            font=("Segoe UI", 9, "italic"),
            fg=SECONDARY_COLOR
        )
        powered_label.pack(side="right", padx=10)

        # Configure grid weights
        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(1, weight=1)

    def update_result_text(self, text):
        """Update the result text widget with the given text."""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)

    def show_error(self, error_msg):
        """Show an error message in the result text widget."""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Error: {error_msg}")

    def process_question(self):
        user_question = self.question_entry.get().strip()
        if not user_question:
            return
            
        if user_question.lower() in ["exit", "e"]:
            self.master.quit()
            return

        # First try to match with SQL intents
        intent = detect_intent(user_question=user_question, intent_docs=self.intent_docs, nlp=self.nlp)

        if intent:
            # Handle SQL query
            query = INTENTS[intent]["query"]
            if self.server is not None and self.database is not None:
                result_df = run_query(str(self.server), str(self.database), query)
                self.display_results(result_df)
            else:
                messagebox.showerror("Connection Error", "Server or database information is missing.")
        else:
            # If no SQL intent matched, use AI model
            if self.ai_available:
                self._handle_ai_question(user_question)
            else:
                messagebox.showwarning("AI Unavailable", 
                    "Sorry, I couldn't understand that question and the AI model is not available. "
                    "Please try rephrasing your question or check if the AI model is properly installed.")

    def _handle_ai_question(self, question: str):
        """Handle questions using the AI model."""
        self.result_text.delete(1.0, tk.END)
        
        # Create loading frame
        loading_frame = tk.Frame(self.result_text)
        loading_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Loading text with spinner
        spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        spinner_label = tk.Label(
            loading_frame,
            text=f"{spinner_frames[0]} AI is thinking...",
            font=("Segoe UI", 14),
            fg=str(ACCENT_COLOR)
        )
        spinner_label.pack(pady=10)
        
        def update_spinner():
            if self.loading_frame is None or not self.loading_frame.winfo_exists():
                return
            
            current_frame = spinner_label.cget("text")[0]
            current_index = spinner_frames.index(current_frame)
            next_index = (current_index + 1) % len(spinner_frames)
            spinner_label.config(text=f"{spinner_frames[next_index]} AI is thinking...")
            self.master.after(100, update_spinner)
        
        def process_ai_response():
            try:
                # Start spinner animation
                update_spinner()
                # Use spaCy-based intent detection for context decision
                detected_intent = detect_intent(user_question=question, intent_docs=self.intent_docs, nlp=self.nlp)
                use_context = detected_intent is not None
                # Pass last_result_summary as extra context if available
                extra_context = getattr(self, 'last_result_summary', '')
                response = self.mistral_handler.generate_response(question, use_context=use_context, extra_context=extra_context)
                # Clear loading animation and show response
                if self.loading_frame is not None and self.loading_frame.winfo_exists():
                    self.loading_frame.destroy()
                    self.loading_frame = None
                # Update the result text in the main thread
                self.master.after(0, lambda: self.update_result_text(response))
            except Exception as e:
                error_msg = f"Error generating response: {str(e)}"
                self.master.after(0, lambda: self.show_error(error_msg))
                if self.loading_frame is not None and self.loading_frame.winfo_exists():
                    self.loading_frame.destroy()
                    self.loading_frame = None
        
        # Store reference to loading frame
        self.loading_frame = loading_frame
        
        # Start AI processing in a separate thread
        threading.Thread(target=process_ai_response, daemon=True).start()

    def display_results(self, result_df):
        self.result_text.delete(1.0, tk.END)
        self.last_result_df = result_df  # Store for export
        # Store a summary string for LLM context (first 5 rows)
        if result_df is not None and not result_df.empty:
            table_str = tabulate(result_df, headers='keys', tablefmt='psql', showindex=False)
            self.result_text.insert(tk.END, table_str)
            # Save a short summary for LLM context (first 5 rows)
            self.last_result_summary = tabulate(result_df.head(5), headers='keys', tablefmt='psql', showindex=False)
        else:
            self.result_text.insert(tk.END, "No results found.")
            self.last_result_summary = None

    def export_results(self):
        if self.last_result_df is None or self.last_result_df.empty:
            messagebox.showwarning("Export", "No results to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            self.last_result_df.to_excel(file_path, index=False)
            messagebox.showinfo("Export", f"Results exported to {file_path}")

    def send_results_email(self):
        if self.last_result_df is None or self.last_result_df.empty:
            messagebox.showwarning("Send to Email", "No results to send.")
            return

        # Create a custom dialog window
        dialog = tk.Toplevel(self.master)
        dialog.title("Send Results via Email")
        dialog.geometry("400x500")
        dialog.configure(bg=BG_COLOR)
        dialog.transient(self.master)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')

        # Create and style the input fields
        frame = tk.Frame(dialog, bg=BG_COLOR, padx=20, pady=30)
        frame.pack(expand=True, fill="both")

        # Recipient email
        tk.Label(frame, text="Recipient Email:", font=("Segoe UI", 11), bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        recipient_entry = tb.Entry(frame, width=40, font=("Segoe UI", 11))
        recipient_entry.pack(fill="x", pady=(0, 20))

        # Sender email
        tk.Label(frame, text="Your Email:", font=("Segoe UI", 11), bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        sender_entry = tb.Entry(frame, width=40, font=("Segoe UI", 11))
        sender_entry.pack(fill="x", pady=(0, 20))

        # Password
        tk.Label(frame, text="Your Password:", font=("Segoe UI", 11), bg=BG_COLOR, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        password_entry = tb.Entry(frame, width=40, font=("Segoe UI", 11), show="*")
        password_entry.pack(fill="x", pady=(0, 30))

        # Buttons frame
        button_frame = tk.Frame(frame, bg=BG_COLOR)
        button_frame.pack(fill="x", pady=(20, 0))

        def on_send():
            recipient = recipient_entry.get().strip()
            sender = sender_entry.get().strip()
            password = password_entry.get().strip()

            if not all([recipient, sender, password]):
                messagebox.showerror("Error", "Please fill in all fields.", parent=dialog)
                return

            # Save DataFrame to a temporary Excel file
            with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
                assert self.last_result_df is not None
                self.last_result_df.to_excel(tmp.name, index=False)
                tmp_path = tmp.name

            SMTP_SERVER = "smtp.gmail.com"
            SMTP_PORT = 587

            msg = EmailMessage()
            msg["Subject"] = "FraudGuard Analysis Results"
            msg["From"] = sender
            msg["To"] = recipient
            msg.set_content("Please find the fraud analysis results attached.")

            with open(tmp_path, "rb") as f:
                file_data = f.read()
                file_name = "results.xlsx"
                msg.add_attachment(file_data, maintype="application", subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=file_name)

            try:
                with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                    server.starttls()
                    server.login(sender, password)
                    server.send_message(msg)
                messagebox.showinfo("Success", f"Results sent to {recipient}", parent=dialog)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send email:\n{e}", parent=dialog)
            finally:
                os.remove(tmp_path)

        # Send button
        send_btn = tb.Button(button_frame, text="Send", command=on_send, 
                           style="success.TButton", width=15)
        send_btn.pack(side="right", padx=(5, 0))

        # Cancel button
        cancel_btn = tb.Button(button_frame, text="Cancel", command=dialog.destroy,
                             style="secondary.TButton", width=15)
        cancel_btn.pack(side="right", padx=(0, 5))

        # Make dialog modal
        dialog.wait_window()

if __name__ == "__main__":
    root = tb.Window(themename="flatly")
    style = tb.Style()
    style.configure("primary.TButton", font=("Segoe UI", 11))
    style.configure("secondary.TButton", font=("Segoe UI", 11))
    # Add Excel-green style for export button
    style.configure(
        "excel.TButton",
        font=("Segoe UI", 11),
        background="#217346",  # Excel green
        foreground="#ffffff",
        bordercolor="#217346",
        focusthickness=3,
        focuscolor="#145a32"
    )
    style.configure(
        "success.TButton",
        font=("Segoe UI", 11),
        background="#EA4335",  # Gmail red
        foreground="#ffffff",
        bordercolor="#EA4335",
        focusthickness=3,
        focuscolor="#C5221F"  # Darker red for focus state
    )
    app = NLPBotApp(root)
    root.mainloop()
