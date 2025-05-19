import React, { createContext, useContext, useState, useEffect } from 'react';
import { Message, Conversation } from '../types';
import { generateMockResponse } from '../utils/mockResponses';

type ChatContextType = {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  messages: Message[];
  activeConversationId: string | null;
  isTyping: boolean;
  sendMessage: (content: string) => void;
  startNewConversation: () => void;
  setActiveConversation: (id: string) => void;
};

const ChatContext = createContext<ChatContextType | undefined>(undefined);

const createEmptyConversation = (): Conversation => {
  const now = new Date();
  return {
    id: crypto.randomUUID(),
    title: 'New conversation',
    messages: [],
    createdAt: now,
    updatedAt: now,
  };
};

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [conversations, setConversations] = useState<Conversation[]>(() => {
    const saved = localStorage.getItem('conversations');
    if (saved) {
      const parsed = JSON.parse(saved);
      return parsed.map((conv: any) => ({
        ...conv,
        createdAt: new Date(conv.createdAt),
        updatedAt: new Date(conv.updatedAt),
        messages: conv.messages.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        })),
      }));
    }
    return [createEmptyConversation()];
  });
  
  const [activeConversationId, setActiveConversationId] = useState<string | null>(() => {
    return conversations[0]?.id || null;
  });
  
  const [isTyping, setIsTyping] = useState(false);

  const currentConversation = conversations.find(c => c.id === activeConversationId) || null;
  const messages = currentConversation?.messages || [];

  useEffect(() => {
    localStorage.setItem('conversations', JSON.stringify(conversations));
  }, [conversations]);

  const updateConversation = (id: string, updates: Partial<Conversation>) => {
    setConversations(prevConversations => 
      prevConversations.map(conv => 
        conv.id === id ? { ...conv, ...updates, updatedAt: new Date() } : conv
      )
    );
  };

  const generateTitle = (message: string): string => {
    // Extract first 30 characters of first message for the title
    return message.slice(0, 30) + (message.length > 30 ? '...' : '');
  };

  const sendMessage = async (content: string) => {
    if (!content.trim() || !activeConversationId) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      content,
      role: 'user',
      timestamp: new Date(),
    };

    // Add user message
    const updatedMessages = [...messages, userMessage];
    updateConversation(activeConversationId, { 
      messages: updatedMessages,
      title: messages.length === 0 ? generateTitle(content) : currentConversation?.title
    });

    // Show typing indicator
    setIsTyping(true);

    // Simulate API delay
    setTimeout(async () => {
      const assistantResponse = await generateMockResponse(content);
      
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        content: assistantResponse,
        role: 'assistant',
        timestamp: new Date(),
      };

      updateConversation(activeConversationId, { 
        messages: [...updatedMessages, assistantMessage] 
      });
      
      setIsTyping(false);
    }, 1000 + Math.random() * 2000); // Random delay between 1-3 seconds
  };

  const startNewConversation = () => {
    const newConversation = createEmptyConversation();
    setConversations([newConversation, ...conversations]);
    setActiveConversationId(newConversation.id);
  };

  const setActiveConversation = (id: string) => {
    setActiveConversationId(id);
  };

  return (
    <ChatContext.Provider value={{
      conversations,
      currentConversation,
      messages,
      activeConversationId,
      isTyping,
      sendMessage,
      startNewConversation,
      setActiveConversation,
    }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = (): ChatContextType => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};