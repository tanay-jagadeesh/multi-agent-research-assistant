from langchain.tools import tool
import logging
import os

@tool
def file_saver(text: str, filename: str = "info.txt") -> str:
    """Saves text to a file. Optionally specify filename."""
    logging.info(f"Saving text to file: {filename}")
    try:
        # Create output directory if it doesn't exist
        os.makedirs("output", exist_ok=True)
        filepath = os.path.join("output", filename)

        with open(filepath, "w") as f:
            f.write(text)
        logging.info("File saved successfully")
        return f"File saved successfully to {filepath}"
    except Exception as e:
        logging.error(f"Error saving file: {e}")
        return f"Error saving file: {e}"
