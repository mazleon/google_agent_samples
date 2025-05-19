import React from 'react';
import { ThemeProvider } from './context/ThemeContext';
import Layout from './components/Layout';
import ChatInterface from './components/ChatInterface';

function App() {
  return (
    <ThemeProvider>
      <Layout>
        <ChatInterface />
      </Layout>
    </ThemeProvider>
  );
}

export default App;