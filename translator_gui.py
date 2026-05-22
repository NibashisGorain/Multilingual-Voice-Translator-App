import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import threading
from translator import take_command, translate_text, speak

# Theme setup
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")
theme = "light"

# Globals
spoken_text = None
last_translated = ""
translation_history = []
listening_animation_running = False

# Language map
language_map = {
    'Arabic': 'ar', 'Bengali': 'bn', 'Chinese': 'zh-cn', 'Dutch': 'nl', 'English': 'en',
    'French': 'fr', 'German': 'de', 'Gujarati': 'gu', 'Hindi': 'hi', 'Italian': 'it',
    'Japanese': 'ja', 'Kannada': 'kn', 'Korean': 'ko', 'Marathi': 'mr', 'Punjabi': 'pa',
    'Russian': 'ru', 'Spanish': 'es', 'Tamil': 'ta', 'Telugu': 'te', 'Turkish': 'tr', 'Urdu': 'ur'
}

# --------------------------- Functions ---------------------------

def animate_listening(step=0):
    if not listening_animation_running:
        return
    dots = '.' * (step % 4)
    output_box.delete("0.0", "end")
    output_box.insert("0.0", f"🎤 Listening{dots}")
    root.after(500, animate_listening, step + 1)


def handle_speak():
    global spoken_text, listening_animation_running
    spoken_text = None
    listening_animation_running = True
    animate_listening()

    def listen():
        global spoken_text, listening_animation_running
        result = take_command()
        spoken_text = result
        listening_animation_running = False
        output_box.delete("0.0", "end")
        typed_input.delete(0, "end")
        if spoken_text:
            output_box.insert("0.0", f"You said: {spoken_text}")
            typed_input.insert(0, "Type your text or use mic 🎤")  # ✅ restore placeholder
        else:
            output_box.insert("0.0", "⚠️ Voice not detected properly.")
            typed_input.insert(0, "Type your text or use mic 🎤")  # ✅ restore placeholder
        
    threading.Thread(target=listen).start()


def handle_translate():
    global last_translated, spoken_text

    input_text = typed_input.get().strip()
    if input_text == 'Type your text or use mic 🎤':
        input_text = ""
    if not input_text:
        if not spoken_text:
            output_box.delete("0.0", "end")
            output_box.insert("0.0", "⚠️ No voice input found!")
            return
        input_text = spoken_text

    target_lang_code = language_map.get(lang_var.get(), 'en')
    translated_text, _ = translate_text(input_text, target_lang_code)
    last_translated = translated_text

    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, translated_text)

    threading.Thread(target=speak, args=(translated_text, target_lang_code)).start()

    # Update history
    history_entry = f"{input_text} → {translated_text}"
    translation_history.append(history_entry)
    if len(translation_history) > 3:
        translation_history.pop(0)
    history_listbox.delete(0, tk.END)
    for item in reversed(translation_history):
        history_listbox.insert(tk.END, item)


def handle_replay():
    if last_translated:
        lang_code = language_map.get(lang_var.get(), 'en')
        speak(last_translated, lang_code)
    else:
        output_box.delete("0.0", "end")
        output_box.insert("0.0", "⚠️ No translation available to speak.")


def handle_history_click(event):
    selection = history_listbox.curselection()
    if selection:
        selected_text = history_listbox.get(selection[0])
        if "→" in selected_text:
            translated = selected_text.split("→")[1].strip()
            lang_code = language_map.get(lang_var.get(), 'en')
            speak(translated, lang_code)


def copy_output():
    root.clipboard_clear()
    root.clipboard_append(output_box.get("0.0", "end").strip())
    output_box.insert("end", "\n✅ Copied!")


def toggle_theme():
    global theme
    theme = "dark" if theme == "light" else "light"
    ctk.set_appearance_mode(theme.capitalize())
    theme_switch.configure(text="Light Mode" if theme == "dark" else "Dark Mode")


def entry_placeholder_in(e):
    if typed_input.get() == "Type your text or use mic 🎤":
        typed_input.delete(0, "end")


def entry_placeholder_out(e):
    if typed_input.get().strip() == "":
        typed_input.insert(0, "Type your text or use mic 🎤")


# --------------------------- GUI ---------------------------

# Create main window
root = ctk.CTk()
root.title("Voice Translator App")
root.geometry("500x650")
root.resizable(False, False)

# Title
ctk.CTkLabel(root, text="🎙️ Voice Translator", font=("Helvetica", 20, "bold")).pack(pady=10)

# Toggle Switch
theme_switch = ctk.CTkSwitch(root, text="Dark Mode", command=toggle_theme)
theme_switch.pack()

# Unified Input + Mic Frame
input_frame = ctk.CTkFrame(root, fg_color="transparent")
input_frame.pack(pady=10)

typed_input = ctk.CTkEntry(input_frame, width=280, font=("Helvetica", 13))
typed_input.insert(0, "Type your text or use mic 🎤")
typed_input.bind("<FocusIn>", entry_placeholder_in)
typed_input.bind("<FocusOut>", entry_placeholder_out)
typed_input.pack(side="left", padx=(10, 5))

mic_btn = ctk.CTkButton(input_frame, text="🎤", width=40, command=handle_speak)
mic_btn.pack(side="left")

# Language Dropdown
ctk.CTkLabel(root, text="Translate to:", font=("Helvetica", 13)).pack()
lang_var = ctk.StringVar(value="English")
lang_dropdown = ttk.Combobox(root, textvariable=lang_var, values=sorted(language_map.keys()), state="readonly", font=("Helvetica", 12))
lang_dropdown.pack(pady=5)

# Translate Button
ctk.CTkButton(root, text="🔘 Translate", font=("Helvetica", 13), command=handle_translate).pack(pady=10)

# Output
ctk.CTkLabel(root, text="Output:", font=("Helvetica", 13)).pack()
output_box = ctk.CTkTextbox(root, height=100, width=400, wrap="word", font=("Consolas", 13))
output_box.pack(pady=5)

#CopyButton
ctk.CTkButton(root, text="📋 Copy", fg_color="#9C27B0", font=("Helvetica", 12), command=copy_output).pack(pady=5)

# Repeat Translation (Speaker) Button
ctk.CTkButton(root, text="🔊 Replay", fg_color="#FF9800", font=("Helvetica", 12), command=handle_replay).pack(pady=5)

# 🕘 History
ctk.CTkLabel(root, text="History (click to replay):", font=("Helvetica", 12)).pack()
history_listbox = tk.Listbox(root, height=4, width=60, font=("Helvetica", 11))
history_listbox.pack(pady=5)
history_listbox.bind("<<ListboxSelect>>", handle_history_click)

# Run app
root.mainloop()
