
````markdown
# Credentia

Credentia is an automated certificate generation and delivery platform designed to simplify the process of creating and distributing personalized certificates at scale.

It takes recipient data from CSV/XLSX files and a certificate template containing dynamic placeholders, generates an individualized certificate for each recipient, converts the certificates to PDF, and automatically delivers them through email.

## Overview

Manually creating and sending hundreds of certificates is repetitive, error-prone, and difficult to manage.

Credentia automates this workflow:

```text
Recipient Data + Certificate Template
                ↓
        Data Validation
                ↓
       Template Detection
                ↓
         Field Mapping
                ↓
    Personalized Certificate
                ↓
          PDF Conversion
                ↓
        Workflow Automation
                ↓
          Gmail Delivery
````

## Features

* Upload recipient data through CSV or XLSX files
* Validate required recipient fields
* Validate email addresses
* Detect duplicate email addresses
* Detect dynamic placeholders in certificate templates
* Map template placeholders to recipient data
* Support multiple dynamic fields such as:

  * `{{Name}}`
  * `{{Course}}`
  * `{{Date}}`
  * `{{Certificate_ID}}`
* Generate individualized certificates for every recipient
* Convert generated PowerPoint certificates to PDF
* Store generated certificate batches
* Serve generated certificates through API endpoints
* Automatically trigger n8n workflows after generation
* Deliver personalized certificates through Gmail
* Handle individual certificate generation failures without stopping the entire batch

## Tech Stack

### Backend

* Python
* FastAPI
* Pandas
* OpenPyXL
* python-pptx
* PyMuPDF
* Pillow
* LibreOffice

### Automation

* n8n
* Gmail API
* Google OAuth 2.0

### Frontend

The frontend is intentionally separated from this repository and can consume the FastAPI API.

## Project Structure

```text
credentia/
│
├── backend/
│   └── app/
│       ├── api/
│       │   └── routes/
│       │       ├── recipients.py
│       │       ├── templates.py
│       │       └── certificates.py
│       │
│       ├── services/
│       │   ├── recipient_service.py
│       │   ├── validator.py
│       │   ├── template_service.py
│       │   ├── mapping_service.py
│       │   ├── certificate_service.py
│       │   ├── pdf_service.py
│       │   ├── batch_service.py
│       │   └── n8n_service.py
│       │
│       └── main.py
│
├── n8n/
│
├── .gitignore
├── README.md
└── requirements.txt
```

## How It Works

### 1. Recipient Data

Credentia accepts CSV or XLSX files containing recipient information.

Example:

| Name         | Email                                         | Course      | Date       | Certificate_ID |
| ------------ | --------------------------------------------- | ----------- | ---------- | -------------- |
| Rahul Sharma | [rahul@example.com](mailto:rahul@example.com) | AI Workshop | 03/10/2026 | CERT-001       |
| Priya Singh  | [priya@example.com](mailto:priya@example.com) | AI Workshop | 03/10/2026 | CERT-002       |

`Name` and `Email` are required fields. Additional columns can be included for custom certificate data.

### 2. Certificate Template

The certificate template is created separately and uploaded to Credentia.

Dynamic values are represented using placeholders:

```text
This certificate is proudly presented to

{{Name}}

for successfully completing

{{Course}}

on {{Date}}.

Certificate ID: {{Certificate_ID}}
```

Credentia detects these placeholders automatically.

### 3. Field Mapping

The detected placeholders are compared against the columns in the recipient data.

For example:

```text
{{Name}}           → Name
{{Course}}         → Course
{{Date}}           → Date
{{Certificate_ID}} → Certificate_ID
```

Unused spreadsheet columns are allowed.

Missing fields required by the template are reported before certificate generation.

### 4. Certificate Generation

For every valid recipient, Credentia creates a personalized copy of the template.

Example:

```text
Rahul_Sharma_CERT-001.pptx
```

The generated certificate is then converted to PDF:

```text
Rahul_Sharma_CERT-001.pdf
```

### 5. Automated Delivery

After successful generation, Credentia sends the batch information to an n8n workflow.

The workflow:

```text
FastAPI
   ↓
n8n Webhook
   ↓
Split recipients
   ↓
Fetch individual certificate PDF
   ↓
Gmail
   ↓
Recipient
```

Each recipient receives their own personalized PDF attachment.

## API

The backend currently exposes endpoints for:

### Recipients

```text
POST /recipients/upload
```

Upload and validate recipient data.

### Templates

```text
POST /templates/upload
```

Upload a certificate template and detect placeholders.

```text
POST /templates/map
```

Map detected placeholders against recipient columns.

### Certificates

```text
POST /certificates/generate
```

Generate a complete certificate batch and trigger the delivery workflow.

```text
GET /certificates/file/{batch_id}/{filename}
```

Retrieve an individual generated certificate.

## Running Locally

### Prerequisites

Make sure the following are installed:

* Python 3.10+
* Node.js
* LibreOffice
* n8n

### Clone the repository

```bash
git clone https://github.com/Yashasvi-023/credentia.git
cd credentia
```

### Create the Python environment

Windows:

```powershell
python -m venv backend/.venv
backend\.venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file and configure the n8n webhook:

```env
N8N_WEBHOOK_URL=http://localhost:5678/webhook-test/credentia-certificates
```

Additional deployment configuration will be documented as the production environment is finalized.

### Start n8n

```bash
n8n
```

### Start FastAPI

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## Gmail Integration

Credentia uses Gmail API with Google OAuth 2.0 for certificate delivery.

No Gmail passwords are stored by the application.

The Gmail account used for development can be replaced with an official organizational Gmail account when the production mailbox is available.

## n8n Integration

n8n is used as the workflow orchestration layer for certificate delivery.

The FastAPI backend sends a batch payload containing:

```json
{
  "batch_id": "example-batch-id",
  "results": [
    {
      "name": "Rahul Sharma",
      "email": "rahul@example.com",
      "certificate_url": "/certificates/file/example-batch-id/Rahul_Sharma_CERT-001.pdf"
    }
  ]
}
```

n8n processes each recipient individually and retrieves the corresponding certificate before sending the email.

## Design Principles

Credentia follows a few core principles:

### Deterministic processing

Certificate generation and validation are handled by deterministic application logic.

### Automation without losing control

The system automates repetitive work while keeping validation and testing steps before mass delivery.

### Separation of responsibilities

FastAPI handles application logic and document generation, while n8n handles workflow orchestration and email delivery.

### Least-privilege integrations

External services such as Gmail are accessed through OAuth rather than storing account passwords.

## Current Status

Credentia currently has a working end-to-end backend pipeline:

```text
CSV/XLSX
   ↓
Validation
   ↓
PPTX Template
   ↓
Placeholder Mapping
   ↓
Personalized Certificates
   ↓
PDF
   ↓
n8n
   ↓
Gmail
   ↓
Recipient
```

The system has been tested with multiple recipients and successfully delivered individualized PDF certificates through Gmail.

## Roadmap

* [ ] Production deployment
* [ ] Production environment configuration
* [ ] Official Gmail account integration
* [ ] Improved batch failure reporting
* [ ] Retry handling for temporary delivery failures
* [ ] AI-assisted field mapping
* [ ] Certificate preview API
* [ ] Custom email templates
* [ ] Certificate verification / QR codes
* [ ] Persistent database and campaign history
* [ ] Additional document formats
* [ ] Additional email providers

## License

License information will be added before the first public release.

````

### One thing before committing this README

Your root `requirements.txt` and `backend/requirements.txt` currently both exist. That's worth cleaning up **before deployment**, because having two dependency manifests can eventually become a tiny dependency goblin.

For now, though, this README is ready to replace the current one.

Then:

```powershell
git add README.md
git commit -m "docs: add project documentation"
git push
````
