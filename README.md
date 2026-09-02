# GRT Transit Data Pipeline

> **Note:** This project is currently a work in progress.

This project builds a local data pipeline to collect, decode, and analyze real-time GTFS (General Transit Feed Specification) data for Grand River Transit (GRT).

> All commands should be run from the root of the project directory.

## Quick Start

1. **Install dependencies**

   Create a virtual environment first:

    **For Mac/Linux:**
   ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

    **For Windows (Command Prompt):**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    ```

    **For Windows (PowerShell):**
    ```bash
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
   ```

   Then install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

2. **Download static feed data**

   Run the downloader script to fetch the baseline GRT scheduled data.

   ```bash
   python src/Static_Feed_Downloader.py
   ```

3. **Collect the data**

   Run the collector script to begin fetching live transit updates. This script runs continuously. Manually terminate the process (`Ctrl+C`) once you've gathered your desired amount of data (the more the better).

   ```bash
   python src/Trip_Updates_Collector.py
   ```

4. **Decode and build the database**

   Process the raw collected data, filling the SQLite database.

   ```bash
   python src/Trip_Updates_Decoder.py
   ```

5. **Run the analysis**

   Open `notebook.ipynb` to run the Python/Pandas SQL queries and view the data visualizations.