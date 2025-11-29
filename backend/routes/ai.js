const express = require('express');
const router = express.Router();
const { analyzeCode, explainCode, fixCode, generateCode } = require('../services/aiService');

// POST /api/ai/analyze - Analyze code
router.post('/analyze', async (req, res) => {
  try {
    const { code } = req.body;
    
    if (!code || code.trim().length === 0) {
      return res.status(400).json({ 
        success: false, 
        error: 'Code is required' 
      });
    }

    const analysis = await analyzeCode(code);
    
    res.json({ 
      success: true, 
      analysis 
    });
  } catch (error) {
    console.error('Analyze route error:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// POST /api/ai/explain - Explain code
router.post('/explain', async (req, res) => {
  try {
    const { code } = req.body;
    
    if (!code || code.trim().length === 0) {
      return res.status(400).json({ 
        success: false, 
        error: 'Code is required' 
      });
    }

    const explanation = await explainCode(code);
    
    res.json({ 
      success: true, 
      explanation 
    });
  } catch (error) {
    console.error('Explain route error:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// POST /api/ai/fix - Fix code
router.post('/fix', async (req, res) => {
  try {
    const { code, error } = req.body;
    
    if (!code || code.trim().length === 0) {
      return res.status(400).json({ 
        success: false, 
        error: 'Code is required' 
      });
    }

    const fixedCode = await fixCode(code, error || 'Fix any errors');
    
    res.json({ 
      success: true, 
      fixedCode 
    });
  } catch (error) {
    console.error('Fix route error:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// POST /api/ai/generate - Generate code
router.post('/generate', async (req, res) => {
  try {
    const { description } = req.body;
    
    if (!description || description.trim().length === 0) {
      return res.status(400).json({ 
        success: false, 
        error: 'Description is required' 
      });
    }

    const generatedCode = await generateCode(description);
    
    res.json({ 
      success: true, 
      code: generatedCode 
    });
  } catch (error) {
    console.error('Generate route error:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

module.exports = router;