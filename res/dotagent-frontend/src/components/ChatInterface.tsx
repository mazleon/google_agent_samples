import React, { useRef, useEffect } from 'react';
import { useChat } from '../context/ChatContext';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

const ChatInterface: React.FC = () => {
  const { messages, currentConversation, isTyping } = useChat();
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-full">
      {messages.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center text-center p-4 md:p-8">
          <h2 className="text-2xl font-bold mb-2">Welcome to DotAgent</h2>
          <p className="text-gray-600 dark:text-gray-400 max-w-md mb-8">
            Your AI assistant ready to help with information, tasks, and conversations.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl w-full">
            {['Tell me a fun fact', 'Write a poem about technology', 
              'Explain quantum computing', 'Help me learn JavaScript'].map((suggestion) => (
              <button
                key={suggestion}
                className="text-left p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <MessageList messages={messages} isTyping={isTyping} />
      )}
      
      <div ref={endOfMessagesRef}></div>
      
      <div className="border-t border-gray-200 dark:border-gray-700 p-4 md:px-8 md:pb-8">
        <MessageInput />
      </div>
    </div>
  );
};

export default ChatInterface;