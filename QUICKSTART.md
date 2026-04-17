# Shadow Engine - Quick Start Guide

## ⚡ 60-Second Setup

### Option 1: Docker (Recommended)
```bash
docker-compose up -d
```
✅ Ready at `http://localhost:8000`

### Option 2: Local Development
```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start Ollama in separate terminal
ollama serve
ollama pull deepseek:8b

# 4. Run Shadow Engine
python -m uvicorn app.main:app --reload
```

## 🧪 Test It Out

### Analyze Sensitive Data
```bash
curl -X POST http://localhost:8000/shadow/analyze \
  -H "Content-Type: application/json" \
  -H "api-key: shadow-dev-key-12345" \
  -d '{
    "raw_data": "Email: john@example.com, SSN: 123-45-6789, Password: SecurePass123!"
  }'
```

### Check Health
```bash
curl http://localhost:8000/health
```

### API Documentation
Visit: `http://localhost:8000/docs` (Swagger UI)
or: `http://localhost:8000/redoc` (ReDoc)

## 📋 What Gets Detected

✅ Personal Data: Emails, phone numbers, SSN, Aadhaar  
✅ Credentials: Passwords, API keys, tokens  
✅ Financial: Credit cards, bank accounts  
✅ Code: Source code, SQL injections  
✅ Medical: Health records, diagnoses  
✅ Business: Confidential information  

## 🎯 Response Format

```json
{
  "classification": ["Financial Data", "PII"],
  "risk_score": 0.95,
  "severity": "CRITICAL",
  "action": "BLOCK",
  "reason": "Critical risk detected",
  "sensitive_entities": [
    {
      "entity_type": "credit_card",
      "value": "****-****-****-1234",
      "confidence": 0.95
    }
  ]
}
```

## 🔧 Configuration

Edit `.env` file or environment variables:
```bash
DEBUG=false
LOG_LEVEL=INFO
LLM_BASE_URL=http://localhost:11434
LLM_MODEL=deepseek:13b
PORT=8000
```

## 📊 View Logs
```bash
tail -f shadow_engine.log
```

## 🚀 Next Steps

1. **Integrate with your app** - Use the API in your application
2. **Custom rules** - Add business-specific detection rules
3. **Feedback loop** - Send feedback to improve accuracy
4. **Deployment** - Deploy to production with proper security

---

Need help? Check `README.md` for detailed documentation.
