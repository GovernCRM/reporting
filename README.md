# 📊 Buildly Dynamic Reporting Tool

This is a Python + Streamlit-based dynamic reporting tool that lets users:

- Authenticate via Buildly Core
- Load data from secured REST endpoints (auto-discovered from Swagger docs)
- Apply flexible filters to any data column
- View charts (bar, line, pie) with custom aggregation
- Export reports to CSV
- Save and reuse filtered reports and visualizations

---

## 🚀 Quickstart

### 1. 📦 Install Dependencies

You need Python 3.8+ with pip. Then:

```bash
git clone https://github.com/buildly-marketplace/reporting-tool.git
cd reporting-tool
python -m venv venv
source venv/bin/activate  # or .\\venv\\Scripts\\activate on Windows
pip install -r requirements.txt
````

### 2. 🔐 Set Up Your `.env` File

Create a `.env` file at the root of the project:

```env
CLIENT_ID=your_buildly_oauth_client_id
CLIENT_SECRET=your_buildly_oauth_client_secret
API_DOCS_URL="https://test.buildly.dev/docs/?format=openapi"
BASE_URL="https://test.buildly.dev"
```

---

### 3. ▶️ Run the App

```bash
streamlit run main.py
```

This will launch the app in your browser at `http://localhost:8501`.

---

## 🛠 Configuration & Usage

### 🔐 Authentication

* You'll be prompted for a Buildly Access Token.
* The token must be a valid JWT from your Buildly Core OAuth client.

### 📡 Loading Data

* After login, select any available `GET` endpoint from the dropdown.
* Data is automatically fetched and displayed in a table.
* Nested JSON data is flattened using `pandas.json_normalize`.

### 🔍 Filtering

* For each column:

  * If the values are limited (≤ 50), a dropdown appears.
  * For high-cardinality fields, a free-text input is shown.
  * Dates can be filtered using a range picker.

### 📈 Visualizations

Once data is loaded, you can:

* Group by any column
* Choose a numeric column for aggregation
* Select an aggregation function: `sum`, `mean`, or `count`
* View:

  * Bar chart
  * Line chart
  * Pie chart
* Save chart configuration as JSON for reuse

### 📤 Export

* Use the "📥 Export to CSV" button to download your filtered results.

---

## 🧪 Testing

You can test the API token by running:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Accept: application/json" \
     https://governcrm-api.buildly.dev/docs/?format=openapi
```

---

## 📁 Project Structure

```
.
├── app/
│   ├── auth.py
│   ├── db.py
│   ├── data_loader.py
│   ├── filters.py
│   └── ui.py
├── main.py
├── requirements.txt
├── Dockerfile (optional)
└── README.md
```

---

## 🐳 Docker (optional)

Build and run the app in Docker:

```bash
docker build -t reporting-tool .
docker run -p 8501:8501 --env-file .env reporting-tool
```

---

## 🤝 Contributing

PRs welcome! Please file issues for bugs or feature requests.

---

## © License

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007 — brought to you by the Buildly team.

