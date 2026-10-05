from app.services.n8n_service import trigger_n8n


result = trigger_n8n(
    "TEST-BATCH-001",
    [
        {
            "name": "Test User",
            "email": "your_email@example.com",
            "certificate_url": "/certificates/file/TEST-BATCH-001/test.pdf"
        }
    ]
)

print(result)