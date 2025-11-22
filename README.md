# The Glow Project - Official Website

The official website for The Glow Project, featuring AI-powered chat and user authentication.

## 🌟 Features

- **Modern Website**: Clean, responsive design showcasing The Glow Project
- **AI Chat**: Interactive chat modal powered by OpenAI
- **User Authentication**: Secure login/signup with Supabase
- **5 Core Pages**:
  - The Glow Foundation
  - Glow Process
  - GlowGPT
  - ARSA Foundation
  - About

## 🛠️ Tech Stack

### Frontend
- **React 19** + **TypeScript**
- **Vite** - Fast build tool
- **React Router** - Navigation
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **Radix UI** - Component primitives
- **Supabase** - Authentication

### Backend
- **FastAPI** - Python web framework
- **OpenAI** - AI chat functionality
- **WebSocket** - Real-time communication

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- Supabase account
- OpenAI API key

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd glowprojectweb
```

2. **Install frontend dependencies**
```bash
npm install
```

3. **Install backend dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the backend directory:
```env
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

5. **Run the development servers**

Frontend:
```bash
npm run dev
```

Backend (in another terminal):
```bash
cd backend
python main.py
```

The website will be available at `http://localhost:5174`

## 📁 Project Structure

```
glowprojectweb/
├── backend/
│   ├── config/          # Configuration
│   ├── models/          # Data schemas
│   ├── routes/          # API routes
│   │   ├── chat.py     # Chat endpoints
│   │   └── streaming.py # WebSocket streaming
│   ├── services/        # Business logic
│   │   ├── chat.py     # Chat service
│   │   └── websocket_manager.py
│   └── main.py         # FastAPI app
├── src/
│   ├── components/
│   │   ├── auth/       # Authentication
│   │   ├── Chat/       # Chat components
│   │   ├── ChatModal.tsx # Chat modal
│   │   ├── Global/     # Shared components
│   │   ├── TheGlowProject/ # Website components
│   │   └── ui/         # UI components
│   ├── context/        # React contexts
│   ├── pages/
│   │   ├── Authentification/ # Login/Profile
│   │   └── TheGlowProject.com/ # Website pages
│   ├── services/       # API client
│   ├── supabase/       # Supabase client
│   └── App.tsx         # Main app
└── public/             # Static assets
```

## 🎨 Development

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

### Lint
```bash
npm run lint
```

## 📝 License

Proprietary - © Isaiah Briggs

## 🔗 Links

- Website: https://theglowproject.com
- Author: Isaiah Briggs

---

**Note**: This is the simplified website version of The Glow Project. For the full GlowGPT application, see the main branch.
