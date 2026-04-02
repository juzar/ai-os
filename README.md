
# AI-OS V4 🚀

## Overview
AI-OS V4 is a production-ready AI DevOps platform with:
- Multi-model support (GPT, Claude, Gemini, Perplexity)
- Kubernetes diagnostics
- GitHub PR review (extensible)
- Memory + context
- CLI + automation

---

## Setup

### 1. Install
```
pip install -r requirements.txt
```

### 2. Configure
```
cp .env.example .env
```

Add your API keys.

---

## Usage

### DevOps
```
python ai/main.py devops "Deploy app"
```

### Incident
```
python ai/main.py incident "API down"
```

### Kubernetes
```
python ai/main.py kube "default"
```

### Perplexity
```
python ai/main.py perplexity "Latest k8s trends"
```

---

## Make CLI global (optional)

Linux/mac:
```
chmod +x ai/main.py
ln -s $(pwd)/ai/main.py /usr/local/bin/ai
```

---

## GitHub Setup
```
git init
git add .
git commit -m "AI OS V4"
git remote add origin https://github.com/juzar/ai-os.git
git push -u origin main
```

---

## CI/CD
Already included in `.github/workflows/ci.yml`
