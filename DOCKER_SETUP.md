# 🐳 Docker + Ollama Setup Guide (100% FREE)

## Why This Solution?

✅ **100% FREE** - No API keys, no billing  
✅ **Unlimited Usage** - Run as many generations as you want  
✅ **Works Offline** - No internet needed after initial download  
✅ **Fast** - Runs locally on your GPU/CPU  
✅ **Private** - Your data never leaves your computer  

---

## Step 1: Install Docker Desktop for Windows

### Download & Install

1. **Download**: https://www.docker.com/products/docker-desktop/
2. **Install** Docker Desktop
3. **Enable WSL 2** (Docker will prompt you)
4. **Restart** your computer

### Verify Installation

Open PowerShell and run:
```powershell
docker --version
```

Should show: `Docker version 24.x.x`

---

## Step 2: Run Ollama in Docker

### Pull Ollama Container

```powershell
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

This command:
- Downloads Ollama (one-time, ~500MB)
- Runs it in background
- Maps port 11434
- Creates persistent storage

### Verify Ollama is Running

```powershell
docker ps
```

Should show `ollama/ollama` container running.

---

## Step 3: Download AI Model

### Option A: Llama 3.2 (3B) - RECOMMENDED for Windows

**Best balance of speed and quality, runs on CPU**

```powershell
docker exec -it ollama ollama pull llama3.2
```

Download size: ~2GB

### Option B: Phi-3 (3.8B) - Faster, smaller

```powershell
docker exec -it ollama ollama pull phi3
```

Download size: ~2.3GB

### Option C: Mistral (7B) - Better quality, needs more RAM

```powershell
docker exec -it ollama ollama pull mistral
```

Download size: ~4.1GB

**Recommendation**: Start with `llama3.2` - it's fast and works great!

---

## Step 4: Test Ollama

```powershell
docker exec -it ollama ollama run llama3.2 "Design a 2-bedroom house"
```

Should respond with house design suggestions!

---

## Step 5: Update Your Backend

### Create Ollama-Compatible Agents

I'll create new agent files that use Ollama instead of Google Gemini.

### Update Environment Variables

Edit `backend/.env`:

```env
# Use Ollama instead of Google Gemini
USE_OLLAMA=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Comment out Google API (not needed)
# GOOGLE_API_KEY=...
```

---

## Model Comparison

| Model | Size | Speed | Quality | RAM Needed |
|-------|------|-------|---------|------------|
| **llama3.2** | 2GB | ⚡⚡⚡ | ⭐⭐⭐⭐ | 4GB |
| phi3 | 2.3GB | ⚡⚡⚡⚡ | ⭐⭐⭐ | 4GB |
| mistral | 4.1GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | 8GB |
| llama3.1 (8B) | 4.7GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | 8GB |

**For Windows without GPU**: Use `llama3.2` or `phi3`

---

## Docker Commands Cheat Sheet

### Start Ollama
```powershell
docker start ollama
```

### Stop Ollama
```powershell
docker stop ollama
```

### Check Status
```powershell
docker ps
```

### View Logs
```powershell
docker logs ollama
```

### Remove Container (if needed)
```powershell
docker stop ollama
docker rm ollama
```

### List Downloaded Models
```powershell
docker exec -it ollama ollama list
```

### Remove a Model
```powershell
docker exec -it ollama ollama rm llama3.2
```

---

## Troubleshooting

### Docker Desktop won't start

**Solution**: Enable Virtualization in BIOS
1. Restart PC
2. Enter BIOS (F2/Del key)
3. Enable Intel VT-x or AMD-V
4. Save and restart

### "WSL 2 installation is incomplete"

**Solution**: Install WSL 2
```powershell
wsl --install
wsl --set-default-version 2
```

Restart computer.

### Port 11434 already in use

**Solution**: Change port mapping
```powershell
docker stop ollama
docker rm ollama
docker run -d -v ollama:/root/.ollama -p 11435:11434 --name ollama ollama/ollama
```

Then update `OLLAMA_BASE_URL=http://localhost:11435` in `.env`

### Model download fails

**Solution**: Check internet connection and retry
```powershell
docker exec -it ollama ollama pull llama3.2
```

---

## Performance Tips

### Speed Up Model Loading

Models load into RAM on first use. Keep Docker running to avoid reload delays.

### Use GPU (if you have NVIDIA)

Install Docker with GPU support:
```powershell
docker run -d --gpus all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

This makes generation **10x faster**!

### Reduce RAM Usage

Use smaller models: `phi3` or `llama3.2:1b`

---

## Expected Performance

### With CPU (16GB RAM):
- **First generation**: 30-45 seconds
- **Subsequent**: 15-25 seconds

### With GPU (NVIDIA):
- **First generation**: 5-10 seconds
- **Subsequent**: 3-5 seconds

### Model Load Time:
- **First request**: +5-10 seconds (one-time)
- **Cached**: Instant

---

## Cost Comparison

| Solution | Cost | Speed | Quality |
|----------|------|-------|---------|
| **Ollama (Docker)** | **$0** | ⚡⚡⚡ | ⭐⭐⭐⭐ |
| Google Gemini Free | $0 | ⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ |
| Google Gemini Paid | $7/1M tokens | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ |
| OpenAI GPT-4 | $30/1M tokens | ⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ |

**Ollama = Unlimited free usage!**

---

## Next Steps

1. Install Docker Desktop
2. Run Ollama container
3. Download `llama3.2` model
4. Test with: `docker exec -it ollama ollama run llama3.2 "Hello"`
5. Tell me when ready, I'll update your backend!

---

## Alternative: Run Ollama Natively (Without Docker)

If you prefer not to use Docker:

1. Download Ollama installer: https://ollama.com/download/windows
2. Install and run
3. Same commands but without `docker exec -it ollama`

Example:
```powershell
ollama pull llama3.2
ollama run llama3.2 "Hello"
```

---

**Ready to proceed? Install Docker and let me know when Ollama is running!** 🚀
