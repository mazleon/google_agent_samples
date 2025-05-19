import React from 'react';
import { Bot } from 'lucide-react';

const TypingIndicator: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto flex gap-4 p-4 rounded-lg">
      <div className="flex-shrink-0">
        <div className="w-8 h-8 bg-teal-100 dark:bg-teal-900 flex items-center justify-center rounded-full">
          <Bot size={18} className="text-teal-600 dark:text-teal-300" />
        </div>
      </div>
      <div className="flex items-center">
        <div className="text-sm font-medium mb-1">DotAgent</div>
        <div className="flex items-center gap-1 ml-2">
          <div className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce" style={{ animationDelay: '100ms' }}></div>
          <div className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce" style={{ animationDelay: '200ms' }}></div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;