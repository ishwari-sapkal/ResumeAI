"""
Compatibility wrapper for ResumeAI.

The actual Flask application is defined in main.py.
Vercel uses main.py as the entry point.

This file is NOT the primary entry point.
"""

from main import app

# This allows local execution with:
# python app.py

if __name__ == "__main__":
    app.run(debug=True)