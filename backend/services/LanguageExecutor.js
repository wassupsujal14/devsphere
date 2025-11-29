const { spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');

class LanguageExecutor {
  constructor() {
    this.tempDir = path.join(__dirname, '..', 'temp');
    this.ensureTempDir();
  }

  async ensureTempDir() {
    try {
      await fs.mkdir(this.tempDir, { recursive: true });
    } catch (err) {
      console.error('Error creating temp directory:', err);
    }
  }

  async executeCode(code, language) {
    const executors = {
      'java': () => this.executeJava(code),
      'python': () => this.executePython(code),
      'cpp': () => this.executeCpp(code),
      'c': () => this.executeC(code),
      'javascript': () => this.executeJavaScript(code)
    };

    const executor = executors[language.toLowerCase()];
    if (!executor) {
      throw new Error(`Language ${language} not supported`);
    }

    return await executor();
  }

  async executeJava(code) {
    // Use your existing Java parser
    const pythonScript = path.join(__dirname, '..', '..', 'parser', 'java_parser.py');
    return new Promise((resolve, reject) => {
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
        if (errorOutput) {
          reject(new Error(errorOutput));
        } else {
          resolve(output.trim());
        }
      });
    });
  }

  async executePython(code) {
    return new Promise((resolve, reject) => {
      const python = spawn('python', ['-c', code]);
      
      let output = '';
      let errorOutput = '';
      
      python.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      python.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });
      
      python.on('close', (exitCode) => {
        if (exitCode !== 0) {
          reject(new Error(errorOutput || 'Python execution failed'));
        } else {
          resolve(output.trim());
        }
      });

      // Timeout after 10 seconds
      setTimeout(() => {
        python.kill();
        reject(new Error('Execution timeout'));
      }, 10000);
    });
  }

  async executeCpp(code) {
    const timestamp = Date.now();
    const sourceFile = path.join(this.tempDir, `temp_${timestamp}.cpp`);
    const outputFile = path.join(this.tempDir, `temp_${timestamp}.exe`);

    try {
      // Write code to file
      await fs.writeFile(sourceFile, code);

      // Compile
      await new Promise((resolve, reject) => {
        const compile = spawn('g++', [sourceFile, '-o', outputFile]);
        let errorOutput = '';

        compile.stderr.on('data', (data) => {
          errorOutput += data.toString();
        });

        compile.on('close', (code) => {
          if (code !== 0) {
            reject(new Error(errorOutput || 'Compilation failed'));
          } else {
            resolve();
          }
        });
      });

      // Execute
      return await new Promise((resolve, reject) => {
        const run = spawn(outputFile);
        let output = '';
        let errorOutput = '';

        run.stdout.on('data', (data) => {
          output += data.toString();
        });

        run.stderr.on('data', (data) => {
          errorOutput += data.toString();
        });

        run.on('close', (code) => {
          if (code !== 0) {
            reject(new Error(errorOutput || 'Runtime error'));
          } else {
            resolve(output.trim());
          }
        });

        setTimeout(() => {
          run.kill();
          reject(new Error('Execution timeout'));
        }, 10000);
      });
    } finally {
      // Cleanup
      try {
        await fs.unlink(sourceFile);
        await fs.unlink(outputFile);
      } catch (err) {
        // Ignore cleanup errors
      }
    }
  }

  async executeC(code) {
    const timestamp = Date.now();
    const sourceFile = path.join(this.tempDir, `temp_${timestamp}.c`);
    const outputFile = path.join(this.tempDir, `temp_${timestamp}.exe`);

    try {
      await fs.writeFile(sourceFile, code);

      // Compile
      await new Promise((resolve, reject) => {
        const compile = spawn('gcc', [sourceFile, '-o', outputFile]);
        let errorOutput = '';

        compile.stderr.on('data', (data) => {
          errorOutput += data.toString();
        });

        compile.on('close', (code) => {
          if (code !== 0) {
            reject(new Error(errorOutput || 'Compilation failed'));
          } else {
            resolve();
          }
        });
      });

      // Execute
      return await new Promise((resolve, reject) => {
        const run = spawn(outputFile);
        let output = '';
        let errorOutput = '';

        run.stdout.on('data', (data) => {
          output += data.toString();
        });

        run.stderr.on('data', (data) => {
          errorOutput += data.toString();
        });

        run.on('close', (code) => {
          if (code !== 0) {
            reject(new Error(errorOutput || 'Runtime error'));
          } else {
            resolve(output.trim());
          }
        });

        setTimeout(() => {
          run.kill();
          reject(new Error('Execution timeout'));
        }, 10000);
      });
    } finally {
      try {
        await fs.unlink(sourceFile);
        await fs.unlink(outputFile);
      } catch (err) {}
    }
  }

  async executeJavaScript(code) {
    return new Promise((resolve, reject) => {
      const node = spawn('node', ['-e', code]);
      
      let output = '';
      let errorOutput = '';
      
      node.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      node.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });
      
      node.on('close', (exitCode) => {
        if (exitCode !== 0) {
          reject(new Error(errorOutput || 'JavaScript execution failed'));
        } else {
          resolve(output.trim());
        }
      });

      setTimeout(() => {
        node.kill();
        reject(new Error('Execution timeout'));
      }, 10000);
    });
  }
}

module.exports = new LanguageExecutor();