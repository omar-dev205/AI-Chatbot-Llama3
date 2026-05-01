import tkinter as tk
from tkinter import scrolledtext, font
import threading
from openai import OpenAI
from config import API_KEY

# ── Configure SambaNova (OpenAI-compatible) ───────────────────────────────────
client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.sambanova.ai/v1"
)
MODEL = "Meta-Llama-3.3-70B-Instruct"
chat_history = []  # manually track conversation

# ── Color Palette ─────────────────────────────────────────────────────────────
BG_DARK       = "#0f0f11"
BG_PANEL      = "#16161a"
BG_INPUT      = "#1e1e24"
BG_USER_MSG   = "#1a1a2e"
BG_BOT_MSG    = "#12121a"
ACCENT        = "#7c6ff7"
ACCENT_HOVER  = "#9d98f5"
TEXT_PRIMARY  = "#e8e8f0"
TEXT_MUTED    = "#6b6b80"
TEXT_USER     = "#c8c5ff"
TEXT_BOT      = "#d0f0e0"
BORDER        = "#2a2a35"
SEND_BTN      = "#5b52e8"
SEND_HOVER    = "#7068f0"

# ── App Window ────────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("O.F AI")
root.geometry("780x680")
root.configure(bg=BG_DARK)
root.resizable(True, True)
root.minsize(500, 500)

# ── Fonts ─────────────────────────────────────────────────────────────────────
font_title   = font.Font(family="Segoe UI", size=13, weight="bold")
font_body    = font.Font(family="Segoe UI", size=11)
font_small   = font.Font(family="Segoe UI", size=9)
font_mono    = font.Font(family="Consolas", size=10)
font_btn     = font.Font(family="Segoe UI", size=11, weight="bold")

# ── Header ────────────────────────────────────────────────────────────────────
header_frame = tk.Frame(root, bg=BG_PANEL, height=64)
header_frame.pack(fill="x", side="top")
header_frame.pack_propagate(False)

dot_canvas = tk.Canvas(header_frame, width=36, height=36,
                        bg=BG_PANEL, highlightthickness=0)
dot_canvas.place(x=18, y=14)
dot_canvas.create_oval(2, 2, 34, 34, fill=ACCENT, outline="")
dot_canvas.create_oval(12, 12, 24, 24, fill=BG_PANEL, outline="")

title_lbl = tk.Label(header_frame, text="O.F AI",
                     font=font_title, bg=BG_PANEL, fg=TEXT_PRIMARY)
title_lbl.place(x=64, y=12)
subtitle_lbl = tk.Label(header_frame, text="Powered by Meta Llama 3.3 70B",
                         font=font_small, bg=BG_PANEL, fg=TEXT_MUTED)
subtitle_lbl.place(x=64, y=36)

status_dot = tk.Canvas(header_frame, width=10, height=10,
                        bg=BG_PANEL, highlightthickness=0)
status_dot.place(relx=1.0, x=-100, y=28)
status_dot.create_oval(1, 1, 9, 9, fill="#3ddc84", outline="")

status_lbl = tk.Label(header_frame, text="Online",
                       font=font_small, bg=BG_PANEL, fg="#3ddc84")
status_lbl.place(relx=1.0, x=-84, y=24)

separator = tk.Frame(root, bg=BORDER, height=1)
separator.pack(fill="x")

# ── Chat Display Area ─────────────────────────────────────────────────────────
chat_outer = tk.Frame(root, bg=BG_DARK)
chat_outer.pack(fill="both", expand=True, padx=0, pady=0)

chat_canvas = tk.Canvas(chat_outer, bg=BG_DARK,
                         highlightthickness=0, bd=0)
scrollbar = tk.Scrollbar(chat_outer, orient="vertical",
                          command=chat_canvas.yview)
chat_canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
chat_canvas.pack(side="left", fill="both", expand=True)

chat_frame = tk.Frame(chat_canvas, bg=BG_DARK)
chat_window = chat_canvas.create_window((0, 0), window=chat_frame,
                                         anchor="nw")

def on_frame_configure(event):
    chat_canvas.configure(scrollregion=chat_canvas.bbox("all"))

def on_canvas_configure(event):
    chat_canvas.itemconfig(chat_window, width=event.width)

chat_frame.bind("<Configure>", on_frame_configure)
chat_canvas.bind("<Configure>", on_canvas_configure)

# ── Mousewheel Scroll ─────────────────────────────────────────────────────────
def on_mousewheel(event):
    chat_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

chat_canvas.bind_all("<MouseWheel>", on_mousewheel)

# ── Message Renderer ──────────────────────────────────────────────────────────
def add_message(role, text):
    is_user = (role == "user")

    outer = tk.Frame(chat_frame, bg=BG_DARK)
    outer.pack(fill="x", padx=20, pady=(6, 2))

    if is_user:
        bubble_bg   = BG_USER_MSG
        text_color  = TEXT_USER
        label_text  = "You"
        label_color = ACCENT
        pad_left    = 120
        pad_right   = 0
    else:
        bubble_bg   = BG_BOT_MSG
        text_color  = TEXT_BOT
        label_text  = "Llama 3"
        label_color = "#3ddc84"
        pad_left    = 0
        pad_right   = 120

    meta_frame = tk.Frame(outer, bg=BG_DARK)
    meta_frame.pack(fill="x")

    meta_lbl = tk.Label(meta_frame, text=label_text,
                         font=font_small, bg=BG_DARK, fg=label_color)
    if is_user:
        meta_lbl.pack(side="right", padx=4)
    else:
        meta_lbl.pack(side="left", padx=4)

    bubble_wrap = tk.Frame(outer, bg=BG_DARK)
    bubble_wrap.pack(fill="x")

    bubble = tk.Frame(bubble_wrap, bg=bubble_bg,
                       highlightthickness=1,
                       highlightbackground=BORDER)
    if is_user:
        bubble.pack(side="right", padx=(pad_left, pad_right))
    else:
        bubble.pack(side="left", padx=(pad_left, pad_right))

    msg_lbl = tk.Label(bubble, text=text, font=font_body,
                        bg=bubble_bg, fg=text_color,
                        wraplength=480, justify="left",
                        padx=14, pady=10, anchor="w")
    msg_lbl.pack()

    root.update_idletasks()
    chat_canvas.yview_moveto(1.0)

# ── Typing Indicator ──────────────────────────────────────────────────────────
typing_frame = None

def show_typing():
    global typing_frame
    typing_frame = tk.Frame(chat_frame, bg=BG_DARK)
    typing_frame.pack(fill="x", padx=20, pady=4, anchor="w")
    dots_lbl = tk.Label(typing_frame, text="Llama 3 is thinking...",
                         font=font_small, bg=BG_DARK, fg=TEXT_MUTED)
    dots_lbl.pack(side="left")
    root.update_idletasks()
    chat_canvas.yview_moveto(1.0)

def hide_typing():
    global typing_frame
    if typing_frame:
        typing_frame.destroy()
        typing_frame = None

# ── Send Message Logic ────────────────────────────────────────────────────────
def send_message(event=None):
    user_text = input_box.get("1.0", "end").strip()
    if not user_text or placeholder_shown[0]:
        return

    input_box.delete("1.0", "end")
    send_btn.config(state="disabled", bg=TEXT_MUTED)
    add_message("user", user_text)
    show_typing()

    # Add user message to history
    chat_history.append({"role": "user", "content": user_text})

    def get_response():
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=chat_history,
                temperature=0.7,
                max_tokens=1024
            )
            reply = response.choices[0].message.content
            # Add assistant reply to history
            chat_history.append({"role": "assistant", "content": reply})
        except Exception as e:
            reply = f"Error: {str(e)}"

        root.after(0, lambda: finish_response(reply))

    def finish_response(reply):
        hide_typing()
        add_message("bot", reply)
        send_btn.config(state="normal", bg=SEND_BTN)

    threading.Thread(target=get_response, daemon=True).start()

# ── Bottom Input Area ─────────────────────────────────────────────────────────
bottom_sep = tk.Frame(root, bg=BORDER, height=1)
bottom_sep.pack(fill="x")

bottom_frame = tk.Frame(root, bg=BG_PANEL, pady=14)
bottom_frame.pack(fill="x", side="bottom")

input_container = tk.Frame(bottom_frame, bg=BG_INPUT,
                            highlightthickness=1,
                            highlightbackground=BORDER)
input_container.pack(fill="x", padx=20, pady=0)

input_box = tk.Text(input_container, height=3, font=font_body,
                     bg=BG_INPUT, fg=TEXT_PRIMARY,
                     insertbackground=ACCENT,
                     relief="flat", bd=0,
                     padx=12, pady=10,
                     wrap="word")
input_box.pack(side="left", fill="both", expand=True)

placeholder_shown = [True]

def show_placeholder():
    input_box.insert("1.0", "Type your message here...")
    input_box.config(fg=TEXT_MUTED)

def on_focus_in(event):
    if placeholder_shown[0]:
        input_box.delete("1.0", "end")
        input_box.config(fg=TEXT_PRIMARY)
        placeholder_shown[0] = False

def on_focus_out(event):
    if not input_box.get("1.0", "end").strip():
        show_placeholder()
        placeholder_shown[0] = True

input_box.bind("<FocusIn>", on_focus_in)
input_box.bind("<FocusOut>", on_focus_out)
show_placeholder()

def on_enter(event):
    if not event.state & 0x1:  # Shift not held
        send_message()
        return "break"

input_box.bind("<Return>", on_enter)

send_btn = tk.Button(input_container, text="Send",
                      font=font_btn, bg=SEND_BTN, fg="white",
                      activebackground=SEND_HOVER,
                      activeforeground="white",
                      relief="flat", bd=0,
                      padx=20, pady=6,
                      cursor="hand2",
                      command=send_message)
send_btn.pack(side="right", padx=8, pady=8)

hint_lbl = tk.Label(bottom_frame,
                     text="Press Enter to send  •  Shift+Enter for new line",
                     font=font_small, bg=BG_PANEL, fg=TEXT_MUTED)
hint_lbl.pack(pady=(4, 0))

# ── Welcome Message ───────────────────────────────────────────────────────────
def show_welcome():
    add_message("bot", "Hello! I'm O.F AI powered by Llama 3. How can I help you today?")

root.after(300, show_welcome)

# ── Run ───────────────────────────────────────────────────────────────────────
root.mainloop()