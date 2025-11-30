
# 🚀 DevSphere - AI-Powered Collaborative Java Development Environment (CloudIDE)

> A modern, full-stack web-based IDE with real-time collaboration, AI-powered code assistance, and advanced compiler visualization

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![MERN Stack](https://img.shields.io/badge/Stack-MERN-blue.svg)](https://www.mongodb.com/mern-stack)
[![AI Powered](https://img.shields.io/badge/AI-Claude-purple.svg)](https://www.anthropic.com/)


---

## 📖 Overview

DevSphere is a comprehensive web-based Integrated Development Environment designed for Java development, featuring AI-powered code analysis, real-time collaboration, and an interactive Abstract Syntax Tree visualizer. Built with the MERN stack and enhanced with cutting-edge AI capabilities.

### ✨ Key Highlights

- 🤖 **AI-Powered Code Assistant** – Intelligent code analysis, explanations, and automatic bug fixes using Claude AI  
- 👥 **Real-Time Collaboration** – Live synchronized coding with chat  
- 🌳 **AST Visualization** – Interactive Abstract Syntax Tree viewer  
- 💻 **Professional Code Editor** – Monaco Editor (VS Code engine)  
- 🔐 **Secure Authentication** – JWT + OAuth2  
- 💾 **Cloud Storage** – Save and manage your Java snippets  

---

## 🎯 Features

### 🖥️ **Advanced Code Editor**
- Monaco Editor integration  
- IntelliSense auto-completion  
- Syntax highlighting  
- Multi-cursor editing  
- Code folding  
- Minimap + customizable themes  

### ⚙️ **Java Compiler & Interpreter**
Supports:
- Classes, objects, and constructors  
- Methods & fields  
- Conditionals and loops  
- Switch statements  
- Arrays + enhanced for-loops  
- Try/catch/finally  
- Operators & expressions  
- OOP features  

### 🤖 **AI Features (Claude API)**
- **Analyze** code quality  
- **Explain** code behavior  
- **Auto-fix** errors  
- **Generate** code from natural language  
- **Visualize AST**  

### 👥 **Real-Time Collaboration**
- Collaboration rooms  
- Live code syncing  
- Chat system  
- User indicators  
- Join via room ID  

### 🌳 **AST Visualization**
- Expandable nodes  
- Color-coded elements  
- Useful for learning compiler internals  

### 🔐 **Authentication & Security**
- JWT login  
- Google & GitHub OAuth  
- Bcrypt hashing  
- Protected API routes  

### 💾 **Code Snippet Management**
- Save, load, and delete snippets  
- User-specific storage  

---

## 🛠️ Tech Stack

### **Frontend**
- React 18  
- Monaco Editor  
- Socket.io Client  
- Lucide React  
- React Router  

### **Backend**
- Node.js + Express  
- MongoDB + Mongoose  
- Socket.io  
- Passport.js  
- JWT & Bcrypt  

### **AI**
- Claude API  
- Python-based Java parser  

---

## 🚀 Installation

### **Prerequisites**
- Node.js 14+  
- MongoDB 4.4+  
- Python 3.8+  
- Git  

---

### **Clone the Repository**

```bash
git clone https://github.com/yourusername/cloudide.git
cd cloudide
```

---

## 🔧 Backend Setup

```bash
cd backend
npm install
```

### Create `.env`:

```bash
cat > .env << EOF
PORT=5000
MONGODB_URI=mongodb://localhost:27017/java-parser
JWT_SECRET=your-jwt-secret-key-here
ANTHROPIC_API_KEY=your-claude-api-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
SESSION_SECRET=your-session-secret
FRONTEND_URL=http://localhost:3000
EOF
```

Start MongoDB:

```bash
mongod
```

Run backend:

```bash
npm run dev
```

---

## 🎨 Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend: http://localhost:3000  
Backend: http://localhost:5000  

---

## 🐍 Python Parser Setup

The Python parser is already integrated — nothing extra needed.

---

## 📚 Usage

1. **Register / Login** using Email or OAuth  
2. **Write Java code** in Monaco Editor  
3. **Run your code**  
4. Use **AI Tools**:
   - Analyze  
   - Explain  
   - Auto-Fix  
   - Generate  
   - AST View  
5. **Collaborate** with team members  
6. **Save snippets**  

---

## 🏗️ Project Structure

```
cloudide/
├── backend/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── middleware/
│   ├── config/
│   ├── server.js
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── App.js
│   │   └── index.js
└── parser/
    └── java_parser.py
```

---

## 🔑 API Endpoints

### **Authentication**
- `POST /api/auth/register`  
- `POST /api/auth/login`  
- `GET /api/auth/user`  
- Google OAuth  
- GitHub OAuth  

### **Code Execution**
- `POST /api/code/execute`  
- `POST /api/code/save`  
- `GET /api/code/snippets`  
- `DELETE /api/code/snippets/:id`  
- `POST /api/code/ast`  

### **AI Features**
- `POST /api/ai/analyze`  
- `POST /api/ai/explain`  
- `POST /api/ai/fix`  
- `POST /api/ai/generate`  

### **WebSocket Events**
- `join-room`  
- `code-change`  
- `chat-message`  
- `user-joined`  
- `user-left`  

---

## 🤝 Contributing

1. Fork repo  
2. Create branch  
3. Commit changes  
4. Push  
5. Create Pull Request  

---

## 📝 Environment Variables

```env
PORT=5000
MONGODB_URI=mongodb://localhost:27017/java-parser
JWT_SECRET=your-super-secret-jwt-key
SESSION_SECRET=your-session-secret-key
ANTHROPIC_API_KEY=sk-ant-your-claude-api-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
FRONTEND_URL=http://localhost:3000
```

---

## 🧪 Testing

```bash
cd backend && npm test
cd frontend && npm test
```

---

## 🐛 Troubleshooting

### MongoDB Errors
- Ensure `mongod` is running  
- Check `.env` values  

### Socket.IO Issues
- Check CORS  
- Ensure backend + frontend running  

### AI Errors
- Verify Claude API key  
- Check backend logs  

---

## 📈 Performance

- ⏱️ Code Execution: <500ms  
- 🤖 AI Response: 2–5s  
- ⚡ Sync Latency: <100ms  
- 👥 Supports 50+ users  

---

## 🔮 Future Enhancements

- [ ] Multi-language support  
- [ ] Version history  
- [ ] Advanced analytics dashboard  
- [ ] Mobile app  
- [ ] Coding challenges  
- [ ] Plugin system  
- [ ] Docker support  
- [ ] CI/CD pipeline  

---

## 📄 License

MIT License — see LICENSE.

---

## 👨‍💻 Author

**Sujal Dusane**  
GitHub: https://github.com/sujaldusane  
LinkedIn: https://www.linkedin.com/in/sujal-dusane/  
Email: dusane.s@northeastern.edu  

---

## 🙏 Acknowledgments

- Claude AI  
- Monaco Editor  
- Socket.io  
- MongoDB  

---

## ⭐ Show Support

If this project helped you, **please star ⭐ the repo!**
