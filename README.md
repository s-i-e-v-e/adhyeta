# अध्येता (adhyētā = student, reader)

अध्येता is an application designed to improve language acquisition skills through the process of reading.

A user can import text files into the application and track their progress on the vocabulary front as they read.

NOTE: The data folder contains material sourced from third parties. Licensing information for each resource is available in the corresponding meta.json.

# Getting Started
The application is written in Python.

* To create a self-contained installation, first install `uv`
  - Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Windows: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
* Run `uv sync` This command installs the required versions of python and other dependencies.
* Run:
  - `uv run ./adhyeta` (Linux)
  - `uv run ./adhyeta.bat` (Windows)
* The app can be accessed on http://127.0.0.1:8000/

# Usage

* Clicking on a word toggles the known/unknown state of the word across the entire library.
* ALT+clicking a word opens a box where you can provide notes/meaning for the word which will then be displayed under the word.
