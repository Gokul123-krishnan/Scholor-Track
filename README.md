<<<<<<< HEAD
# Scholar Track – Scholarship Management System

A modern, responsive, and student-focused web application built with **Python (Flask)**, **SQLite3**, **HTML5**, **CSS3**, **JavaScript**, and **Bootstrap 5**.

Scholar Track empowers students to discover, organize, manage, and track scholarship opportunities, eligibility requirements, application deadlines, and statuses in one centralized dashboard.

---

## 1. Key Features

- **Dynamic Analytics Dashboard:**
  - Real-time statistics: Total scholarships, Active/Upcoming, Expiring Soon (&le; 7 days), and Expired.
  - Multi-segment progress visual for application status distribution.
  - Financial overview tracking awarded/approved grant amounts versus total funding pool.
  - Prioritized lists for urgent approaching deadlines and recently added opportunities.

- **Complete Scholarship Management (CRUD):**
  - **Create:** Add new scholarship entries with name, provider, description, eligibility criteria, grant amount, deadline, official portal URL, and initial status.
  - **Read:** Browse the full scholarship directory and view rich detail pages for each opportunity.
  - **Update:** Edit all scholarship details or quickly change status from anywhere.
  - **Delete:** Safely remove scholarship records with a modal confirmation dialog to prevent accidental deletion.

- **Search, Filter & Sort:**
  - Real-time keyword search by scholarship name, provider organization, or description.
  - Filter by application status (`Pending`, `Applied`, `Approved`, `Rejected`).
  - Filter by deadline timeline (`Active & Upcoming`, `Expiring Soon`, `Expired Deadlines`).
  - Sort by deadline (nearest or furthest), funding amount (highest or lowest), name (A-Z), or newest added.

- **Intelligent Deadline Tracking:**
  - Automatically compares deadlines against the current date (`YYYY-MM-DD`).
  - Dynamic visual badges:
    - **Active & Upcoming:** Green badge showing days remaining.
    - **Expiring Soon (&le; 7 days):** Amber/Red pulsing badge warning students of impending due dates.
    - **Expired:** Red badge showing days elapsed since the deadline passed.

- **Application Status Tracking:**
  - 4 distinct tracking states:
    - <span style="color:#d97706; font-weight:bold;">Pending</span> &ndash; Under consideration or document preparation.
    - <span style="color:#4f46e5; font-weight:bold;">Applied</span> &ndash; Application submitted to provider.
    - <span style="color:#059669; font-weight:bold;">Approved</span> &ndash; Scholarship successfully awarded!
    - <span style="color:#dc2626; font-weight:bold;">Rejected</span> &ndash; Not selected for this cycle.
  - Quick dropdowns on the directory table and details page allow immediate status updates.

- **User-Friendly Responsive Interface:**
  - Collapsible sidebar navigation for seamless desktop, tablet, and mobile experiences.
  - Clean typography and professional palette (Deep Navy, Indigo, Emerald Green, Amber).
  - Dismissible flash notification alerts for feedback on every user action.

---

## 2. Technology Stack

| Component | Technology | Description |
|---|---|---|
| **Backend** | Python 3.9+ / Flask 3.x | Lightweight, robust web framework and routing |
| **Database** | SQLite 3 (`sqlite3` module) | Serverless, zero-configuration local relational database |
| **Frontend Framework** | Bootstrap 5.3 + Bootstrap Icons | Modern, mobile-first responsive layout and icon system |
| **Custom Styling** | CSS3 (`static/css/style.css`) | Custom card designs, color variables, pulse animations |
| **Client Scripting** | JavaScript (ES6) | Mobile drawer toggle, delete modal binder, auto-dismiss alerts |
| **Templating** | Jinja2 | Reusable layout inheritance (`base.html`) and context processors |

---

## 3. Database Schema

The SQLite database file `scholarships.db` is initialized automatically on first startup.

### `scholarships` Table

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique record identifier |
| `scholarship_name` | TEXT | NOT NULL | Official name of the scholarship |
| `provider` | TEXT | NOT NULL | Hosting organization, company, or institution |
| `description` | TEXT | NULLABLE | Detailed description and scholarship benefits |
| `eligibility` | TEXT | NULLABLE | Academic, demographic, or degree requirements |
| `amount` | REAL | NOT NULL DEFAULT 0.0 | Funding or award amount in USD |
| `deadline` | TEXT | NOT NULL | Application deadline in `YYYY-MM-DD` format |
| `application_link` | TEXT | NULLABLE | Direct URL to the official portal |
| `application_status` | TEXT | NOT NULL DEFAULT 'Pending' | `Pending`, `Applied`, `Approved`, or `Rejected` |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

> **Note on Sample Data:** If the database table is empty on startup, the application automatically seeds realistic sample records (Google, Microsoft, Tata Trust, Adobe, Reliance Foundation, etc.) with relative dates so you can immediately see active, urgent, and expired deadlines without manual data entry.

---

## 4. Project Directory Structure

```text
Scholar Track/
├── app.py                      # Flask application entrypoint & HTTP routes
├── database.py                 # SQLite initialization, sample seed & CRUD queries
├── requirements.txt            # Python package dependencies
├── scholarships.db             # SQLite database (auto-generated)
├── README.md                   # Complete documentation & execution guide
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Master layout with sidebar, navbar & modals
│   ├── index.html              # Main dashboard with statistics & urgent deadlines
│   ├── scholarships.html       # Full directory with search, filter, and sort
│   ├── add_scholarship.html    # Form to create new scholarship records
│   ├── edit_scholarship.html   # Form to edit existing scholarship records
│   ├── scholarship_details.html# Comprehensive detail view of a single scholarship
│   ├── 404.html                # Friendly 404 Not Found error page
│   └── 500.html                # Friendly 500 Server Error page
└── static/                     # Static assets
    ├── css/
    │   └── style.css           # Custom styling, color themes & responsive rules
    └── js/
        └── script.js           # Modal handlers, drawer toggle & interactivity
```

---

## 5. Visual Studio Code Setup and Execution (Windows)

Follow these steps to run Scholar Track locally on Windows using VS Code:

### Step 1: Open the Project in VS Code
1. Launch **Visual Studio Code**.
2. Go to **File &gt; Open Folder...** and select the `Scholar Track` folder:
   ```text
   d:\Scholar Track
   ```
3. Open a new terminal inside VS Code:
   - Press **``Ctrl + ` ``** (Control + Backtick) OR click **Terminal &gt; New Terminal** from the top menu.

---

### Step 2: Check Python Installation
Verify that Python (3.9 or higher) is installed on your Windows machine:
```bash
python --version
```
*Expected output: `Python 3.x.x`*

---

### Step 3: Create and Activate Virtual Environment
Create a dedicated virtual environment named `venv`:
```bash
python -m venv venv
```

Activate the virtual environment:
- In **PowerShell**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- In **Command Prompt (CMD)**:
  ```cmd
  venv\Scripts\activate.bat
  ```
*(When activated, you will see `(venv)` at the beginning of your terminal prompt).*

> **PowerShell Execution Policy Tip:** If you encounter an error like `cannot be loaded because running scripts is disabled on this system`, run this command in your PowerShell terminal and retry activation:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> .\venv\Scripts\Activate.ps1
> ```

---

### Step 4: Install Dependencies
Install Flask and other required packages using `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

### Step 5: Run the Flask Application
Start the local development server:
```bash
python app.py
```

You should see output similar to:
```text
============================================================
 Scholar Track - Scholarship Management System
 Server running locally at: http://127.0.0.1:5000/
 Press CTRL+C to stop the server.
============================================================
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

---

### Step 6: Open the Application in Your Browser
Open your favorite web browser (Chrome, Edge, Firefox) and navigate to:
```
http://127.0.0.1:5000/
```
Or simply hold **`Ctrl`** and click the link displayed in the VS Code terminal.

To stop the server at any time, press **`Ctrl + C`** in the terminal.

---

## 6. Common Errors and Troubleshooting

| Problem | Cause | Solution |
|---|---|---|
| `'python' is not recognized as an internal or external command` | Python is not added to the Windows system `PATH` variable. | Reinstall Python from [python.org](https://www.python.org/) and make sure to check the box **"Add Python to PATH"** during setup. |
| `Activate.ps1 cannot be loaded because running scripts is disabled` | Windows PowerShell default execution policy blocks unsigned scripts. | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in the VS Code terminal before activating `venv`. |
| `Address already in use: Port 5000` | Another application or previous Flask process is still running on port 5000. | Change the port in `app.py` (e.g. `app.run(..., port=5001)`) or terminate the existing process using Task Manager. |
| `TemplateNotFound: base.html` | Flask was started from an incorrect working directory. | Make sure your terminal prompt is in the project root directory (`d:\Scholar Track`) before executing `python app.py`. |
| `sqlite3.OperationalError: database is locked` | An external SQLite viewer (like DB Browser) opened the database file with an exclusive lock. | Close any external database viewer program or restart the Flask server. |

---

## 7. License and Attribution

Developed as a demonstration and student project for academic and personal scholarship tracking. Free to modify and adapt for college submissions and educational purposes.
=======
# Scholor-Track
>>>>>>> 7cc34e7a8db3d5dda116af93843b3d3d2d0ec95f
