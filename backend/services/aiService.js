const Anthropic = require('@anthropic-ai/sdk');

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// Analyze Java code
async function analyzeCode(code) {
  try {
    console.log('🤖 Analyzing with Claude...');
    
    const message = await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 2000,
      messages: [{
        role: 'user',
        content: `You are an expert Java code analyzer. Analyze this code and respond with ONLY a JSON object (no markdown, no extra text).

JSON structure required:
{
  "hasErrors": true/false,
  "errors": ["error1", "error2"],
  "warnings": ["warning1", "warning2"],
  "suggestions": ["suggestion1", "suggestion2"],
  "rating": "Excellent/Good/Fair/Poor",
  "summary": "brief summary"
}

Java Code to analyze:
\`\`\`java
${code}
\`\`\`

Return ONLY the JSON object.`
      }]
    });

    const responseText = message.content[0].text;
    console.log('✅ Claude responded');
    
    // Extract JSON from response
    const jsonMatch = responseText.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const analysis = JSON.parse(jsonMatch[0]);
      return analysis;
    }

    // Fallback if JSON not found
    return {
      hasErrors: false,
      errors: [],
      warnings: [],
      suggestions: [responseText.substring(0, 200)],
      rating: 'Good',
      summary: 'Analysis completed'
    };

  } catch (error) {
    console.error('Claude Analysis Error:', error.message);
    throw new Error('Failed to analyze code with AI');
  }
}

// Explain code
async function explainCode(code) {
  try {
    console.log('🤖 Explaining with Claude...');
    
    const message = await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1500,
      messages: [{
        role: 'user',
        content: `You are a Java programming teacher. Explain what this code does in simple, clear terms. Be educational and easy to understand.

Java Code:
\`\`\`java
${code}
\`\`\`

Provide a clear, step-by-step explanation.`
      }]
    });

    return message.content[0].text;

  } catch (error) {
    console.error('Claude Explain Error:', error.message);
    throw new Error('Failed to explain code with AI');
  }
}

// Fix code errors
async function fixCode(code, errorDescription) {
  try {
    console.log('🤖 Fixing with Claude...');
    
    const message = await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 2000,
      messages: [{
        role: 'user',
        content: `You are a Java code fixer. Fix the errors in this code and return ONLY the corrected Java code (no explanations, no markdown blocks, just pure Java code).

${errorDescription ? `Error to fix: ${errorDescription}` : 'Fix any errors you find'}

Code:
\`\`\`java
${code}
\`\`\`

Return ONLY the fixed Java code.`
      }]
    });

    let fixedCode = message.content[0].text;
    
    // Remove markdown code blocks if present
    fixedCode = fixedCode.replace(/```java\n?/g, '');
    fixedCode = fixedCode.replace(/```\n?/g, '');
    fixedCode = fixedCode.trim();
    
    return fixedCode;

  } catch (error) {
    console.error('Claude Fix Error:', error.message);
    throw new Error('Failed to fix code with AI');
  }
}

// Generate code from description
async function generateCode(description) {
  try {
    console.log('🤖 Generating with Claude...');
    
    const message = await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 2000,
      messages: [{
        role: 'user',
        content: `You are a Java code generator. Create Java code based on this description. Include a complete working program with main method if appropriate. Add helpful comments.

Description: ${description}

Return ONLY the Java code (no explanations, no markdown blocks, just pure Java code).`
      }]
    });

    let generatedCode = message.content[0].text;
    
    // Remove markdown code blocks if present
    generatedCode = generatedCode.replace(/```java\n?/g, '');
    generatedCode = generatedCode.replace(/```\n?/g, '');
    generatedCode = generatedCode.trim();
    
    return generatedCode;

  } catch (error) {
    console.error('Claude Generate Error:', error.message);
    throw new Error('Failed to generate code with AI');
  }
}

module.exports = {
  analyzeCode,
  explainCode,
  fixCode,
  generateCode
};