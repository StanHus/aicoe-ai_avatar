# 🤖 AI Avatar Chatbot - Pluggable Voice Assistant

A real-time AI avatar that speaks with users through a photorealistic talking head. Currently configured as a Trilogy AI expert, but easily adaptable to any knowledge domain.

---

## 🚀 **Quick Start Options**

### **Option 1: One-Command Docker (Recommended)**

```bash
# Clone and enter directory
git clone [your-repo]
cd chatbot-video

# Start everything with one command
./start-simple.sh
```

**What this does:**

- ✅ Starts backend in Docker container
- ✅ Starts frontend locally
- ✅ Opens at http://localhost:3000
- ✅ Backend API at http://localhost:8080

### **Option 2: Local Development**

```bash
# Terminal 1 - Backend
npm run start-agent

# Terminal 2 - Frontend
npm run start-app
```

### **Option 3: Full Docker (Advanced)**

```bash
# For complete containerization
docker-compose up --build
```

---

## ⚙️ **Making It Your Own**

### **Option 1: Use Your Content Feed**

Edit `backend/config.py`:

```python
FEED_URL = "https://yourcompany.com/blog/feed.xml"
EXPERT_DOMAIN = "Your Company"
VOICE = "onyx"  # alloy, echo, fable, onyx, nova, shimmer
AVATAR_IMAGE = "assets/your-avatar.png"
```

### **Option 2: Replace the AI Entirely**

Create your own chatbot class in `ai_chatbot.py`:

```python
class YourAIChatbot:
    async def initialize(self) -> str:
        return "Your greeting message"

    async def get_response(self, user_message: str) -> str:
        # Your AI logic here
        return "Your response"
```

---

## 🏗️ **2-Layer Architecture**

### **Layer 1: Avatar Service** (`avatar_service.py`)

Handles all voice/video presentation:

- LiveKit room management
- Hedra photorealistic avatar
- OpenAI Realtime API for speech
- Generic framework - works with any AI

### **Layer 2: AI Chatbot** (`ai_chatbot.py`)

Provides the intelligence:

- Text in → Text out interface
- Currently: Trilogy AI expert with 41 articles
- Easily replaceable with OpenAI, Claude, or custom AI

### **How They Work Together**

1. User speaks → Avatar captures audio
2. Speech-to-text → Converts to text query
3. Text sent to AI layer → Gets response
4. Text-to-speech → Avatar speaks with lip sync
5. Result: Natural conversation with visual avatar

## 🔧 **Setup Requirements**

Create `.env` file:

```env
OPENAI_API_KEY=sk-proj-xxx
HEDRA_API_KEY=sk_hedra_xxx
LIVEKIT_URL=wss://xxx.livekit.cloud
LIVEKIT_API_KEY=APIxxx
LIVEKIT_API_SECRET=xxx
```

## 📁 **Project Structure**

```
backend/
├── avatar_service.py    # Layer 1: Avatar presentation
├── ai_chatbot.py       # Layer 2: AI intelligence
├── config.py           # Easy customization
frontend/               # Next.js web interface
```

**Current Configuration**: Trilogy AI Expert with 42 research articles  
**Architecture**: 2-layer backend (Avatar Service + AI Chatbot)  
**Customization**: Replace AI chatbot or update config.py for your Substack domain
