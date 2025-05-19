// This file contains mock responses for the assistant
// To be replaced with actual API integration in the future

export const generateMockResponse = async (message: string): Promise<string> => {
  // Simple mock response generator
  if (message.toLowerCase().includes('hello') || message.toLowerCase().includes('hi')) {
    return "Hello! I'm DotAgent, your AI assistant. How can I help you today?";
  }
  
  if (message.toLowerCase().includes('how are you')) {
    return "I'm functioning optimally, thank you for asking! How can I assist you today?";
  }
  
  if (message.toLowerCase().includes('help')) {
    return "I'm DotAgent, an AI assistant designed to help answer questions, have conversations, and assist with various tasks. What would you like to know or discuss?";
  }

  if (message.toLowerCase().includes('code') || message.toLowerCase().includes('programming')) {
    return "Here's an example of a simple React component:\n\n```jsx\nimport React from 'react';\n\nconst HelloWorld = () => {\n  return (\n    <div className=\"greeting\">\n      <h1>Hello, World!</h1>\n      <p>Welcome to React</p>\n    </div>\n  );\n};\n\nexport default HelloWorld;\n```\n\nIs there a specific programming topic you'd like to learn about?";
  }

  // Default response
  return "As an AI assistant, I'm here to help answer questions, have conversations, and assist with various tasks. While I don't have real-time internet access, I've been trained on a wide variety of information. Is there something specific you'd like to know or discuss?";
};