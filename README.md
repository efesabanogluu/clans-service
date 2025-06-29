# 🛡️ Clans API

A Flask-based REST API that manages clan creation, listing, retrieval, and deletion operations. This project was developed as part of a technical case study and is production-ready with deployment to Google Cloud Run and a MySQL backend via Cloud SQL.

---

## 🚀 Features

- RESTful API for clan management (`POST`, `GET`, `DELETE`)
- UUID-based identification
- MySQL database access using connection pooling
- Cloud SQL connection via Unix socket
- Cloud-native deployment using Cloud Run + GitHub Actions
- Logging and error handling included

---

## 🧩 API Endpoints

| Method | Endpoint             | Description                        |
|--------|----------------------|------------------------------------|
| GET    | `/`                  | Welcome route with API overview    |
| POST   | `/clans`             | Create a new clan                  |
| GET    | `/clans`             | List all clans, optional filters   |
| GET    | `/clans/<uuid:id>`   | Get clan by ID                     |
| DELETE | `/clans/<uuid:id>`   | Delete clan by ID                  |

---

## 🛠️ Technology Stack

- **Backend**: Python 3.9 + Flask
- **Database**: Cloud SQL (MySQL)
- **Hosting**: Google Cloud Run (containerized)
- **CI/CD**: GitHub Actions
- **Containerization**: Docker + Gunicorn

---

## ⚙️ Setup (Local Development)

1. Clone the repository:
   ```bash
   git clone https://github.com/efesabanogluu/clans-api.git
   cd clans-api
   
### 2. Configure environment variables

Create a `.env` file in the root directory or export them manually:

```env
DB_SOCKET=/cloudsql/YOUR_PROJECT:REGION:INSTANCE
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=vertigo_db
```

### 3. Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

The API will run at: [http://localhost:8080](http://localhost:8080)

---

## 🐳 Running with Docker

```bash
docker build -t clans-api .
docker run -p 8080:8080 --env-file .env clans-api
```

---

## ☁️ Deploy to Google Cloud Run (CI/CD)

This project includes a fully automated GitHub Actions pipeline:  
📄 [`deploy-to-cloud-run.yml`](./deploy-to-cloud-run.yml)

### ✔️ What it does:
- Authenticates to GCP using a service account
- Builds and pushes Docker image to Artifact Registry
- Deploys image to Cloud Run
- Connects to Cloud SQL via Unix socket
- Injects secrets as environment variables

### 🔐 Required GitHub Secrets:

| Secret Name       | Description                          |
|-------------------|--------------------------------------|
| `GCP_PROJECT_ID`  | Your GCP project ID                  |
| `GCP_SA_KEY`      | Base64-encoded service account JSON  |
| `DB_USER`         | MySQL username                       |
| `DB_PASSWORD`     | MySQL password                       |
| `DB_NAME`         | MySQL database name (e.g., `vertigo_db`) |
| `DB_SOCKET`       | Cloud SQL socket path (e.g., `/cloudsql/project:region:instance`) |

> Push to `master` triggers auto-deploy.

---

## 🧪 API Testing

You can use `curl`, Postman, or any REST client.

### Example: Create a new clan

```bash
curl -X POST http://localhost:8080/clans \
  -H 'Content-Type: application/json' \
  -d '{"name": "Guardians", "region": "EU"}'
```

### Example: List clans sorted by name

```bash
curl "http://localhost:8080/clans?sort=name"
```

---

## 📦 File Structure

```
clans-api/
├── app.py                             # Main Flask application
├── config.py                          # DB config (optional)
├── requirements.txt                   # Python dependencies
├── Dockerfile                         # Docker image definition
├── .github/
│   └── workflows/
│       └── deploy-to-cloud-run.yml    # GitHub Actions workflow
└── README.md                          # This file
```


## SQL Schema

The `clans` table is created using the following SQL script:

```sql
CREATE TABLE clans (
  id CHAR(36) NOT NULL,
  name VARCHAR(100) NOT NULL,
  region VARCHAR(2) DEFAULT NULL,
  created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

### Key Features:
1. **UUID Primary Key**  
   - `id CHAR(36)` stores UUIDs in standard 36-character format (e.g. `123e4567-e89b-12d3-a456-426614174000`)

2. **Constraints**  
   - `name` is required (`NOT NULL`) with max 100 characters  
   - `region` is optional (2-letter country code like `TR`, `US`)  
   - `created_at` automatically sets to UTC timestamp on insert  

3. **Optimized for Cloud SQL (MySQL)**  
   - Uses `InnoDB` storage engine  
   - `utf8mb4` encoding supports all Unicode characters  
   - Case-insensitive collation (`utf8mb4_0900_ai_ci`)  
