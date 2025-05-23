# Generative AI Models Manager

This project is a small desktop application that uses a Tkinter GUI to fetch, display, and manage generative AI models from the Google Generative AI API. The application stores an API key and model data locally in an SQLite database (app_data.db) and highlights new or updated models.

## Features

- Fetches available generative AI models using your API key.
- Displays model information in a user-friendly GUI.
- Highlights new models (yellow) and updated models (light green).
- Stores API key and model details in a local SQLite database.
- Updates only those models that have changed since the last fetch.

## Requirements

- Python 3.x
- [Tkinter](https://docs.python.org/3/library/tkinter.html) (usually included with Python)
- [SQLite3](https://docs.python.org/3/library/sqlite3.html) (usually included with Python)
- The `google.genai` client library to interact with the Generative AI API.  
  (You may need to install this package—check the official documentation for installation instructions.)

## Usage

Simply run the application script:
```
python  main.py.py
```
Replace ` main.py.py` with the name of your main Python file. The application will perform the following operations on startup:

- Create a local SQLite database (if it doesn’t already exist) with tables to store your API key and model details.
- Prompt you for your API key if it is not already saved.
- Fetch the latest available generative AI models using the saved API key.
- Update the database by adding new models or updating existing ones only if changes are detected.
- Launch a Tkinter-based GUI where you can:
  - View available models in a list.
  - See detailed information about a selected model.
  - Identify visually which models are new or have been updated (highlighted).

## Project Structure

- `app_data.db`  
  The local SQLite database used for storing the API key and model details.

- ` main.py.py`  
  The main Python script that:
  - Creates the database and tables (if needed)
  - Loads/saves the API key and models
  - Connects to the Google Generative AI API to list available models
  - Implements a GUI using Tkinter

- `README.md`  
  This file.

## Customization & Contribution

Feel free to fork this repository and improve the project by adding features or refactoring the code. Contributions of any kind are welcome. Please submit issues or pull requests through GitHub.

## Command-Line Interface

A simple CLI is provided in `cli.py` to list available models without using the GUI.
After ensuring your API key is stored (e.g., via your database retrieval logic), install dependencies:
```bash
pip install -r requirements.txt
```
Run the CLI to fetch and display model information:
```bash
python cli.py list-models
```
This will print each model's JSON fields to stdout.