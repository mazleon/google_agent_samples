import React from 'react';
import { useChat } from '../context/ChatContext';
import { MessageSquarePlus, MessageSquare, Trash2 } from 'lucide-react';

interface SidebarProps {
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ onClose }) => {
  const { conversations, activeConversationId, startNewConversation, setActiveConversation } = useChat();

  const handleConversationClick = (id: string) => {
    setActiveConversation(id);
    onClose(); // Close sidebar on mobile after selecting a conversation
  };

  return (
    <div className="flex flex-col h-full pb-4">
      <div className="p-4">
        <button
          onClick={() => {
            startNewConversation();
            onClose();
          }}
          className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white py-2 px-4 rounded-lg transition-colors"
        >
          <MessageSquarePlus size={18} />
          <span>New Chat</span>
        </button>
      </div>

      <div className="px-2 text-sm text-gray-500 dark:text-gray-400 uppercase font-semibold my-2">
        Conversations
      </div>

      <div className="flex-1 overflow-y-auto px-2 space-y-1">
        {conversations.map((conversation) => (
          <button
            key={conversation.id}
            onClick={() => handleConversationClick(conversation.id)}
            className={`w-full flex items-center px-3 py-2 text-left rounded-md transition-colors ${
              activeConversationId === conversation.id
                ? 'bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-300'
                : 'hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            <MessageSquare size={16} className="mr-2 flex-shrink-0" />
            <span className="truncate flex-1">{conversation.title}</span>
            {activeConversationId !== conversation.id && (
              <Trash2 
                size={16} 
                className="opacity-0 group-hover:opacity-100 text-gray-500 hover:text-red-500 transition-opacity"
                onClick={(e) => {
                  e.stopPropagation();
                  // Delete functionality would go here
                }}
              />
            )}
          </button>
        ))}
      </div>

      <div className="px-4 mt-auto pt-4 text-xs text-center text-gray-500 dark:text-gray-400">
        DotAgent v1.0.0 • © 2025
      </div>
    </div>
  );
};

export default Sidebar;