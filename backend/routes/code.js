const express = require('express');
const router = express.Router();
const { spawn } = require('child_process');
const path = require('path');
const authMiddleware = require('../middleware/auth');
const languageExecutor = require('../services/languageExecutor');

// Code Schema
const mongoose = require('mongoose');
const CodeSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  title: String,
  code: String,
  output: String,
  createdAt: { type: Date, default: Date.now }
});

const Code = mongoose.model('Code', CodeSchema);

// @route   POST /api/code/execute
// @desc    Execute Java code
// @access  Public (can be protected with authMiddleware)
/*router.post('/execute', async (req, res) => {
  const { code } = req.body;
  
  const pythonScript = path.join(__dirname, '..', '..', 'parser', 'java_parser.py');
  const python = spawn('python', [pythonScript]);
  
  let output = '';
  let errorOutput = '';
  
  python.stdin.write(code);
  python.stdin.end();
  
  python.stdout.on('data', (data) => {
    output += data.toString();
  });
  
  python.stderr.on('data', (data) => {
    errorOutput += data.toString();
  });
  
  python.on('close', (code) => {
    if (code !== 0 || errorOutput) {
      return res.status(400).json({ 
        success: false, 
        error: errorOutput || 'Execution failed' 
      });
    }
    
    res.json({ 
      success: true, 
      output: output.trim() 
    });
  });
});*/

router.post('/execute', async (req, res) => {
  try {
    const { code, language = 'java' } = req.body;
    
    if (!code || code.trim().length === 0) {
      return res.status(400).json({ 
        success: false, 
        error: 'Code is required' 
      });
    }

    console.log(`Executing ${language} code...`);
    const output = await languageExecutor.executeCode(code, language);
    
    res.json({ 
      success: true, 
      output: output || 'Program executed successfully (no output)'
    });
  } catch (error) {
    console.error('Execution error:', error);
    res.status(400).json({ 
      success: false, 
      error: error.message || 'Execution failed' 
    });
  }
});

// @route   POST /api/code/save
// @desc    Save code snippet
// @access  Private
router.post('/save', authMiddleware, async (req, res) => {
  try {
    const { title, code, output } = req.body;
    const newCode = new Code({ 
      userId: req.user.id,
      title, 
      code, 
      output 
    });
    await newCode.save();
    res.json({ success: true, message: 'Code saved!', id: newCode._id });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// @route   GET /api/code/snippets
// @desc    Get user's saved snippets
// @access  Private
router.get('/snippets', authMiddleware, async (req, res) => {
  try {
    const snippets = await Code.find({ userId: req.user.id }).sort({ createdAt: -1 });
    res.json({ success: true, snippets });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// @route   GET /api/code/snippets/:id
// @desc    Get single snippet
// @access  Private
router.get('/snippets/:id', authMiddleware, async (req, res) => {
  try {
    const snippet = await Code.findOne({ 
      _id: req.params.id, 
      userId: req.user.id 
    });
    if (!snippet) {
      return res.status(404).json({ success: false, error: 'Snippet not found' });
    }
    res.json({ success: true, snippet });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// @route   DELETE /api/code/snippets/:id
// @desc    Delete snippet
// @access  Private
router.delete('/snippets/:id', authMiddleware, async (req, res) => {
  try {
    await Code.findOneAndDelete({ 
      _id: req.params.id, 
      userId: req.user.id 
    });
    res.json({ success: true, message: 'Snippet deleted' });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});



router.post('/ast', async (req, res) => {
  try {
    const { code } = req.body;
    
    if (!code || code.trim().length === 0) {
      return res.status(400).json({ 
        success: false, 
        error: 'Code is required' 
      });
    }

    const pythonScript = path.join(__dirname, '..', '..', 'parser', 'java_parser.py');
    
    // Run with --ast flag to get AST JSON
    const python = spawn('python', [pythonScript, '--ast']);
    
    let output = '';
    let errorOutput = '';
    
    python.stdin.write(code);
    python.stdin.end();
    
    python.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    python.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });
    
    python.on('close', (code) => {
      if (code !== 0 || errorOutput) {
        return res.status(400).json({ 
          success: false, 
          error: errorOutput || 'AST generation failed' 
        });
      }
      
      try {
        const ast = JSON.parse(output);
        res.json({ 
          success: true, 
          ast 
        });
      } catch (e) {
        res.status(500).json({
          success: false,
          error: 'Failed to parse AST'
        });
      }
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

module.exports = router;
