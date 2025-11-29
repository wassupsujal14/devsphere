const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const http = require('http');
const socketIO = require('socket.io');
require('dotenv').config();
const session = require('express-session');
const passport = require('./config/passport'); 

const app = express();
const server = http.createServer(app);

// Socket.IO setup with CORS
/*const io = socketIO(server, {
  cors: {
    origin: "http://localhost:3000",
    methods: ["GET", "POST"],
    credentials: true
  }
});

// Middleware
//app.use(cors());
//app.use(express.json());
// Middleware
app.use(cors({
  origin: 'http://localhost:3000',
  credentials: true
}));*/

// Update CORS to allow your production frontend:
const io = socketIO(server, {
  cors: {
    origin: process.env.FRONTEND_URL || "http://localhost:3000",
    methods: ["GET", "POST"],
    credentials: true
  }
});

app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true
}));
app.use(express.json());

// Session middleware for OAuth
app.use(session({
  secret: process.env.SESSION_SECRET || 'secret',
  resave: false,
  saveUninitialized: false,
  cookie: { secure: false }  // Set to true in production with HTTPS
}));

// MongoDB Connection
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/java-parser')
  .then(() => console.log('✅ MongoDB Connected'))
  .catch(err => console.log('❌ MongoDB Error:', err));

// Routes
app.use('/api/auth', require('./routes/auth'));
app.use('/api/code', require('./routes/code'));
app.use('/api/ai', require('./routes/ai'));
app.use(passport.initialize());
app.use(passport.session());


// Health check
app.get('/', (req, res) => {
  res.json({ 
    message: 'Java Parser API is running!',
    status: 'OK',
    endpoints: {
      auth: '/api/auth/register, /api/auth/login',
      code: '/api/code/execute, /api/code/save, /api/code/snippets, /api/code/ast',
      ai: '/api/ai/analyze, /api/ai/explain, /api/ai/fix, /api/ai/generate',
      collab: 'WebSocket on /'
    }
  });
});

// ===========================
// COLLABORATION LOGIC
// ===========================

// Store active rooms and users
const rooms = new Map(); // roomId -> { code, users: [{ id, username, cursor }] }

io.on('connection', (socket) => {
  console.log('🔌 User connected:', socket.id);

  // Join a collaboration room
  socket.on('join-room', ({ roomId, username }) => {
    socket.join(roomId);
    
    // Initialize room if doesn't exist
    if (!rooms.has(roomId)) {
      rooms.set(roomId, {
        code: `public class Main {
    public static void main(String[] args) {
        int x = 10;
        int y = 20;
        println("Sum: " + (x + y));
    }
}`,
        users: []
      });
    }

    const room = rooms.get(roomId);
    
    // Add user to room
    const user = {
      id: socket.id,
      username: username,
      cursor: null,
      color: getRandomColor()
    };
    
    room.users.push(user);
    
    // Send current code to the new user
    socket.emit('room-joined', {
      code: room.code,
      users: room.users
    });
    
    // Notify others that a new user joined
    socket.to(roomId).emit('user-joined', user);
    
    console.log(`✅ ${username} joined room ${roomId}`);
  });

  // Handle code changes
  socket.on('code-change', ({ roomId, code }) => {
    const room = rooms.get(roomId);
    if (room) {
      room.code = code;
      // Broadcast to all users in the room except sender
      socket.to(roomId).emit('code-update', { code });
    }
  });

  // Handle cursor position changes
  socket.on('cursor-change', ({ roomId, cursor }) => {
    const room = rooms.get(roomId);
    if (room) {
      const user = room.users.find(u => u.id === socket.id);
      if (user) {
        user.cursor = cursor;
        socket.to(roomId).emit('cursor-update', {
          userId: socket.id,
          cursor
        });
      }
    }
  });

  // Handle chat messages
  socket.on('chat-message', ({ roomId, message, username }) => {
    io.to(roomId).emit('chat-message', {
      username,
      message,
      timestamp: new Date().toISOString()
    });
  });

  // Handle disconnect
  socket.on('disconnect', () => {
    console.log('🔌 User disconnected:', socket.id);
    
    // Remove user from all rooms
    rooms.forEach((room, roomId) => {
      const userIndex = room.users.findIndex(u => u.id === socket.id);
      if (userIndex !== -1) {
        const user = room.users[userIndex];
        room.users.splice(userIndex, 1);
        
        // Notify others
        io.to(roomId).emit('user-left', {
          userId: socket.id,
          username: user.username
        });
        
        // Delete room if empty
        if (room.users.length === 0) {
          rooms.delete(roomId);
        }
      }
    });
  });
});

// Helper function
function getRandomColor() {
  const colors = [
    '#ef4444', '#f59e0b', '#10b981', '#3b82f6', 
    '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'
  ];
  return colors[Math.floor(Math.random() * colors.length)];
}

// Start server (use server.listen instead of app.listen!)
const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
  console.log(`🔌 WebSocket ready for collaboration`);
});


