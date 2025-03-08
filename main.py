import sqlite3
import tkinter as tk
from tkinter import scrolledtext, Listbox, SINGLE, END, simpledialog, messagebox
from google import genai


def create_db():
    """Create a SQLite database and tables if they don't exist."""
    conn = sqlite3.connect("app_data.db")
    c = conn.cursor()

    # Create table for storing API key
    c.execute('''CREATE TABLE IF NOT EXISTS api_key (
                    id INTEGER PRIMARY KEY,
                    key TEXT)''')

    # Create table for storing models
    c.execute('''CREATE TABLE IF NOT EXISTS models (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    display_name TEXT,
                    description TEXT,
                    version TEXT,
                    input_token_limit INTEGER,
                    output_token_limit INTEGER)''')

    conn.commit()
    conn.close()


def load_api_key():
    """Loads the API key from the SQLite database."""
    conn = sqlite3.connect("app_data.db")
    c = conn.cursor()
    c.execute("SELECT key FROM api_key WHERE id = 1")
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


def save_api_key(api_key):
    """Saves the API key to the SQLite database."""
    conn = sqlite3.connect("app_data.db")
    c = conn.cursor()

    # Insert or update the API key
    c.execute("INSERT OR REPLACE INTO api_key (id, key) VALUES (1, ?)", (api_key,))
    conn.commit()
    conn.close()
    return True


def save_models(models):
    """Saves the list of models to the SQLite database only if there are new or updated models."""
    conn = sqlite3.connect("app_data.db")
    c = conn.cursor()

    for model in models:
        c.execute("SELECT * FROM models WHERE name = ?", (model["Name"],))
        existing_model = c.fetchone()

        if not existing_model:
            # Model is new, so insert it
            c.execute('''INSERT INTO models 
                (name, display_name, description, version, input_token_limit, output_token_limit)
                VALUES (?, ?, ?, ?, ?, ?)''',
                (model["Name"], model["Display Name"], model["Description"], model["Version"],
                model["Input Token Limit"], model["Output Token Limit"]))
        else:
            # Compare values using the correct indices from the database tuple:
            update_needed = False
            if (existing_model[2] != model["Display Name"] or 
                existing_model[3] != model["Description"] or 
                existing_model[4] != model["Version"] or 
                existing_model[5] != model["Input Token Limit"] or 
                existing_model[6] != model["Output Token Limit"]):
                update_needed = True

            if update_needed:
                c.execute('''UPDATE models
                SET display_name = ?, description = ?, version = ?, 
                input_token_limit = ?, output_token_limit = ?
                WHERE name = ?''',
                (model["Display Name"], model["Description"], model["Version"],
                model["Input Token Limit"], model["Output Token Limit"], model["Name"]))
        
    conn.commit()
    conn.close()


def get_existing_models():
    """Fetches all existing models from the database."""
    conn = sqlite3.connect("app_data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM models")
    models = c.fetchall()
    conn.close()
    return models


def list_available_models(api_key, text_widget, listbox):
    """Lists available generative AI models and displays them in a GUI, saving new models to the database."""
    try:
        client = genai.Client(api_key=api_key)
        models = client.models.list()

        if models:
            listbox.delete(0, END)
            model_data = []

            # Get existing models from the database
            existing_models = get_existing_models()
            existing_model_names = {model[1] for model in existing_models}  # Set of model names

            # Flag for highlighting changes
            new_or_updated_models = []

            for model in models:
                model_info = {
                    "Name": model.name,
                    "Display Name": model.display_name,
                    "Description": model.description,
                    "Version": model.version,
                    "Input Token Limit": model.input_token_limit,
                    "Output Token Limit": model.output_token_limit
                }

                # "Ghost" model comparison logic
                if model.name not in existing_model_names:
                    # Model is new (not in DB)
                    new_or_updated_models.append((model.display_name, "new"))
                else:
                    # Model exists, we will compare it with the database
                    for existing_model in existing_models:
                        if existing_model[1] == model.name:
                            ghost_model = {
                                "Name": model.name,
                                "Display Name": model.display_name,
                                "Description": model.description,
                                "Version": model.version,
                                "Input Token Limit": model.input_token_limit,
                                "Output Token Limit": model.output_token_limit
                            }
                        if (existing_model[2] != ghost_model["Display Name"] or
                            existing_model[3] != ghost_model["Description"] or
                            existing_model[4] != ghost_model["Version"] or
                            existing_model[5] != ghost_model["Input Token Limit"] or
                            existing_model[6] != ghost_model["Output Token Limit"]):
                            new_or_updated_models.append((model.display_name, "updated"))
                        break

                listbox.insert(END, model.display_name)
                model_data.append(model_info)

            # Save only the new or updated models to the database
            save_models(model_data)

            def on_select(event):
                selected_index = listbox.curselection()
                if selected_index:
                    selected_display_name = listbox.get(selected_index[0])
                    model_info = next(model for model in model_data if model["Display Name"] == selected_display_name)
                    text_widget.delete(1.0, END)
                    for key, value in model_info.items():
                        text_widget.insert(END, f"{key}: {value}\n")

            listbox.bind('<<ListboxSelect>>', on_select)

            # Highlight new or updated models
            for index in range(listbox.size()):
                model_display_name = listbox.get(index)
                for name, status in new_or_updated_models:
                    if model_display_name == name:
                        listbox.itemconfig(index, {'bg': 'yellow' if status == "new" else 'lightgreen'})

            # Notify the user if there are new or updated models
            if new_or_updated_models:
                new_models = [name for name, status in new_or_updated_models if status == "new"]
                updated_models = [name for name, status in new_or_updated_models if status == "updated"]
                message = ""
                if new_models:
                    message += f"New models added: {', '.join(new_models)}\n"
                if updated_models:
                    message += f"Updated models: {', '.join(updated_models)}"
                messagebox.showinfo("Model Update", message)
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
                nonlocal api_key  # allows the outside api_key to be modified.
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
    # Create the database if it doesn't exist
    create_db()

    api_key = load_api_key()
    if api_key is None:
        api_key = simpledialog.askstring("API Key", "Enter your API key:")
        if api_key:
            save_api_key(api_key)
        else:
            exit()
    create_gui(api_key)
