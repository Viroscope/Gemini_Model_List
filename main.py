from google import genai
import tkinter as tk
from tkinter import scrolledtext, Listbox, SINGLE, END, simpledialog, messagebox
import json
import os

def load_api_key():
    """Loads the API key from a local keyfile."""
    try:
        with open("api_key.json", "r") as f:
            data = json.load(f)
            return data.get("api_key")
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None

def save_api_key(api_key):
    """Saves the API key to a local keyfile."""
    try:
        with open("api_key.json", "w") as f:
            json.dump({"api_key": api_key}, f)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save API key: {e}")
        return False

def list_available_models(api_key, text_widget, listbox):
    """Lists available generative AI models and displays them in a GUI."""
    try:
        client = genai.Client(api_key=api_key)
        models = client.models.list()

        if models:
            listbox.delete(0, END)
            model_data = {}

            for model in models:
                listbox.insert(END, model.display_name)
                model_data[model.display_name] = {
                    "Name": model.name,
                    "Display Name": model.display_name,
                    "Description": model.description,
                    "Version": model.version,
                    "Input Token Limit": model.input_token_limit,
                    "Output Token Limit": model.output_token_limit,
                }
            def on_select(event):
                selected_index = listbox.curselection()
                if selected_index:
                    selected_display_name = listbox.get(selected_index[0])
                    model_info = model_data[selected_display_name]
                    text_widget.delete(1.0, END)
                    for key, value in model_info.items():
                        text_widget.insert(END, f"{key}: {value}\n")
            listbox.bind('<<ListboxSelect>>', on_select)

        else:
            text_widget.insert(END, "No models found.")

    except Exception as e:
        text_widget.insert(END, f"An error occurred: {e}")

def create_gui(api_key):
    """Creates the GUI window."""
    window = tk.Tk()
    window.title("Generative AI Models")

    def settings():
        new_api_key = simpledialog.askstring("API Key", "Enter your API key:", initialvalue=load_api_key())
        if new_api_key:
            if save_api_key(new_api_key):
                messagebox.showinfo("Success", "API key saved.")
                nonlocal api_key #allows the outside api key to be modified.
                api_key = new_api_key
                listbox.delete(0, END)
                text_widget.delete(1.0, END)
                list_available_models(api_key, text_widget, listbox)

    menubar = tk.Menu(window)
    settings_menu = tk.Menu(menubar, tearoff=0)
    settings_menu.add_command(label="Settings", command=settings)
    menubar.add_cascade(label="File", menu=settings_menu)
    window.config(menu=menubar)

    listbox_frame = tk.Frame(window)
    listbox_frame.pack(side=tk.LEFT, fill=tk.Y)

    listbox = Listbox(listbox_frame, selectmode=SINGLE, width=60)
    listbox.pack(fill=tk.Y, expand=True)

    scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)

    text_frame = tk.Frame(window)
    text_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD)
    text_widget.pack(fill=tk.BOTH, expand=True)

    list_available_models(api_key, text_widget, listbox)

    window.mainloop()

if __name__ == "__main__":
    api_key = load_api_key()
    if api_key is None:
        api_key = simpledialog.askstring("API Key", "Enter your API key:")
        if api_key:
            save_api_key(api_key)
        else:
            exit()
    create_gui(api_key)