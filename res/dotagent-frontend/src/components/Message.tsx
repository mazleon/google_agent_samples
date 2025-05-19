import React, { useState, useEffect } from 'react';
import { Message as MessageType } from '../types';
import { User, Bot, Copy, Volume2, ThumbsUp, ThumbsDown, Check } from 'lucide-react';

interface MessageProps {
  message: MessageType;
}

const Message: React.FC<MessageProps> = ({ message }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [copied, setCopied] = useState(false);
  const [liked, setLiked] = useState<boolean | null>(null);
  const isUser = message.role === 'user';

  useEffect(() => {
    // Start the animation after component mount
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  // Format timestamp
  const formatTime = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    }).format(date);
  };

  // Copy message content to clipboard
  const copyToClipboard = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Text-to-speech
  const speak = () => {
    if ('speechSynthesis' in window) {
      // Cancel any ongoing speech
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(message.content);
      window.speechSynthesis.speak(utterance);
    }
  };

  // Handle like/dislike
  const handleFeedback = (isPositive: boolean) => {
    setLiked(isPositive);
    // Here you would typically send this feedback to your backend
    console.log(`Message ${message.id} was ${isPositive ? 'liked' : 'disliked'}`);
  };

  // Function to render content with code blocks
  const renderContent = (content: string) => {
    // Split by code blocks
    const parts = content.split(/(```[\s\S]*?```)/g);
    
    return parts.map((part, index) => {
      // Check if this part is a code block
      if (part.startsWith('```') && part.endsWith('```')) {
        const codeContent = part.slice(3, -3);
        const languageMatch = codeContent.match(/^([a-z]+)\n/);
        let language = '';
        let code = codeContent;
        
        if (languageMatch) {
          language = languageMatch[1];
          code = codeContent.slice(language.length + 1);
        }
        
        return (
          <pre key={index} className="my-2 p-4 bg-gray-100 dark:bg-gray-800 rounded-md overflow-x-auto">
            <code>{code}</code>
          </pre>
        );
      }
      
      // Regular text
      return (
        <p key={index} className="whitespace-pre-wrap">
          {part}
        </p>
      );
    });
  };

  return (
    <div
      className={`transition-opacity duration-300 ease-in ${
        isVisible ? 'opacity-100' : 'opacity-0'
      } ${!isUser ? 'bg-gray-50 dark:bg-gray-800/50' : ''} w-full`}
    >
      <div className={`max-w-4xl ${isUser ? 'ml-auto' : 'mr-auto'} flex ${isUser ? 'flex-row-reverse' : 'flex-row'} gap-4 p-4 rounded-lg`}>
        <div className="flex-shrink-0">
          {isUser ? (
            <div className="w-8 h-8 bg-primary-100 dark:bg-primary-900 flex items-center justify-center rounded-full">
              <User size={18} className="text-primary-600 dark:text-primary-300" />
            </div>
          ) : (
            <div className="w-8 h-8 bg-teal-100 dark:bg-teal-900 flex items-center justify-center rounded-full">
              <Bot size={18} className="text-teal-600 dark:text-teal-300" />
            </div>
          )}
        </div>
        <div className={`flex-1 ${isUser ? 'text-right' : 'text-left'}`}>
          <div className="mb-1 flex items-center justify-between text-sm">
            <span className="font-medium">{isUser ? 'You' : 'DotAgent'}</span>
            <span className="text-gray-500 dark:text-gray-400 text-xs">
              {formatTime(message.timestamp)}
            </span>
          </div>
          <div className={`${isUser ? 'bg-primary-50 dark:bg-primary-900/30 border border-primary-100 dark:border-primary-800' : 'bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700'} p-3 rounded-lg shadow-message text-gray-800 dark:text-gray-200 leading-relaxed ${isUser ? 'text-left' : ''}`}>
            {renderContent(message.content)}
          </div>
          
          {/* Action buttons - only for assistant messages */}
          {!isUser && (
            <div className="flex items-center mt-2 space-x-2 text-gray-500 dark:text-gray-400">
              <button 
                onClick={copyToClipboard}
                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
                title="Copy to clipboard"
              >
                {copied ? <Check size={16} className="text-green-500" /> : <Copy size={16} />}
              </button>
              <button 
                onClick={speak}
                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
                title="Text to speech"
              >
                <Volume2 size={16} />
              </button>
              <div className="ml-auto flex items-center space-x-1">
                <button 
                  onClick={() => handleFeedback(true)}
                  className={`p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors ${liked === true ? 'text-green-500' : ''}`}
                  title="Like"
                >
                  <ThumbsUp size={16} />
                </button>
                <button 
                  onClick={() => handleFeedback(false)}
                  className={`p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors ${liked === false ? 'text-red-500' : ''}`}
                  title="Dislike"
                >
                  <ThumbsDown size={16} />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Message;