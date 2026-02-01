import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { chatApi } from '../utils/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  Scale, Menu, X, Plus, Send, Bookmark, Copy, Download, LogOut,
  Settings, HelpCircle, FileText, Mic, Paperclip, Trash2, Search,
  PanelLeft, PanelLeftClose, Briefcase
} from 'lucide-react';
import { toast } from 'sonner';
import { ThemeSwitcher } from '../components/ThemeSwitcher';
import { VoiceInput } from '../components/VoiceInput';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { themes, currentTheme } = useTheme();
  const theme = themes[currentTheme];
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [currentChat, setCurrentChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadChatHistory();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChatHistory = async () => {
    try {
      const history = await chatApi.getHistory();
      setChatHistory(history);
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const handleNewChat = () => {
    setCurrentChat(null);
    setMessages([]);
  };

  const handleLoadChat = async (chatId) => {
    try {
      const chat = await chatApi.getChat(chatId);
      setCurrentChat(chat);
      setMessages(chat.messages || []);
    } catch (error) {
      toast.error('Error loading chat');
    }
  };

  const handleDeleteChat = async (chatId, e) => {
    e.stopPropagation();
    try {
      await chatApi.deleteChat(chatId);
      toast.success('Chat deleted');
      setChatHistory(chatHistory.filter(c => c.id !== chatId));
      if (currentChat?.id === chatId) {
        handleNewChat();
      }
    } catch (error) {
      toast.error('Error deleting chat');
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || loading) return;

    const userMessage = {
      sender: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages([...messages, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await chatApi.sendMessage(inputMessage, currentChat?.id);

      setMessages(prev => [...prev, response.ai_message]);

      if (!currentChat) {
        setCurrentChat({ id: response.chat_id });
        await loadChatHistory();
      }
    } catch (error) {
      toast.error('Error sending message');
      console.error('Send message error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleVoiceTranscript = (transcript) => {
    setInputMessage(prev => prev + ' ' + transcript);
  };

  const handleCopyMessage = (content) => {
    navigator.clipboard.writeText(content);
    toast.success('Copied to clipboard');
  };

  const handleExportChat = async (format) => {
    if (!currentChat?.id) {
      toast.error('No chat to export');
      return;
    }

    try {
      const blob = await chatApi.exportChat(currentChat.id, format);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `chat_${currentChat.id}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success(`Chat exported as ${format.toUpperCase()}`);
    } catch (error) {
      toast.error('Error exporting chat');
      console.error('Export error:', error);
    }
  };

  const handleLiveCase = () => {
    toast.info('Live Case Feature', {
      description: 'Create a dedicated group space for in-depth case resolution. This feature will track a case until it is fully solved. (Coming Soon)'
    });
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const quickPrompts = [
    "Draft a legal notice",
    "Explain property law",
    "Analyze a contract",
    "Indian Constitution rights"
  ];

  return (
    <div className="flex h-screen bg-gray-50" data-testid="dashboard">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 bg-white border-r border-gray-200 flex flex-col overflow-hidden`}>
        {/* Sidebar Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Scale className="w-6 h-6" style={{ color: theme.primary }} />
              <span className="font-bold text-gray-900">Pleader AI</span>
            </div>
            {/* ChatGPT-style Sidebar Toggle Button */}
            <button
              onClick={() => setSidebarOpen(false)}
              className="p-2 rounded-lg hover:bg-gray-100 transition-all duration-200 group"
              data-testid="sidebar-close-button"
              title="Close sidebar"
            >
              <PanelLeftClose
                className="w-5 h-5 text-gray-500 group-hover:text-gray-700 transition-colors"
              />
            </button>
          </div>

          <Button
            onClick={handleNewChat}
            className="w-full text-white"
            style={{ backgroundColor: theme.primary }}
            data-testid="new-chat-button"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Chat
          </Button>
        </div>

        {/* User Info */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <Avatar>
              <AvatarImage src={user?.avatar_url} />
              <AvatarFallback style={{ backgroundColor: theme.background, color: theme.primaryDark }}>
                {user?.name?.charAt(0).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{user?.name}</p>
              <p className="text-xs text-gray-500 truncate">{user?.email}</p>
            </div>
          </div>
        </div>

        {/* Chat History */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="mb-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input
                placeholder="Search chats..."
                className="pl-9 h-9 text-sm"
                data-testid="search-chats"
              />
            </div>
          </div>

          <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">Recent Chats</h3>
          <div className="space-y-1">
            {chatHistory.map((chat) => (
              <div
                key={chat.id}
                onClick={() => handleLoadChat(chat.id)}
                className={`flex items-center justify-between p-3 rounded-lg cursor-pointer group ${currentChat?.id === chat.id ? 'border' : 'hover:bg-gray-50'}`}
                style={currentChat?.id === chat.id ? { backgroundColor: theme.background, borderColor: theme.hover } : {}}
                data-testid={`chat-item-${chat.id}`}
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{chat.title}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(chat.updated_at).toLocaleDateString()}
                  </p>
                </div>
                <button
                  onClick={(e) => handleDeleteChat(chat.id, e)}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-50 rounded"
                  data-testid={`delete-chat-${chat.id}`}
                >
                  <Trash2 className="w-4 h-4 text-red-500" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Sidebar Menu */}
        <div className="p-4 border-t border-gray-200 space-y-1">
          <button
            onClick={handleLiveCase}
            className="w-full flex items-center space-x-3 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg group"
            data-testid="live-case-link"
          >
            <Briefcase className="w-5 h-5 text-purple-600 group-hover:text-purple-700" />
            <span className="font-medium text-purple-700">Live Case</span>
          </button>
          <button
            onClick={() => navigate('/analyze')}
            className="w-full flex items-center space-x-3 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
            data-testid="analyze-docs-link"
          >
            <FileText className="w-5 h-5" />
            <span>Analyze Documents</span>
          </button>
          <button
            onClick={() => navigate('/settings')}
            className="w-full flex items-center space-x-3 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
            data-testid="settings-link"
          >
            <Settings className="w-5 h-5" />
            <span>Settings</span>
          </button>
          <button
            onClick={() => navigate('/help')}
            className="w-full flex items-center space-x-3 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
            data-testid="help-link"
          >
            <HelpCircle className="w-5 h-5" />
            <span>Help & Support</span>
          </button>
          <button
            onClick={handleLogout}
            className="w-full flex items-center space-x-3 px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg"
            data-testid="logout-button"
          >
            <LogOut className="w-5 h-5" />
            <span>Logout</span>
          </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col" data-testid="chat-area">
        {/* Chat Header */}
        <div className="bg-white border-b border-gray-200 p-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {/* Sidebar Open Button - Only visible when sidebar is closed (ChatGPT style) */}
            {!sidebarOpen && (
              <button
                onClick={() => setSidebarOpen(true)}
                className="p-2 rounded-lg hover:bg-gray-100 transition-all duration-200 group"
                data-testid="sidebar-open-button"
                title="Open sidebar"
              >
                <PanelLeft
                  className="w-5 h-5 text-gray-500 group-hover:text-gray-700 transition-colors"
                />
              </button>
            )}
            <div className="flex items-center space-x-2">
              <Scale className="w-6 h-6" style={{ color: theme.primary }} />
              <h1 className="text-lg font-semibold text-gray-900">Pleader AI</h1>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <ThemeSwitcher />
            {currentChat && messages.length > 0 && (
              <div className="relative group">
                <Button variant="ghost" size="sm" className="text-gray-600" data-testid="export-button">
                  <Download className="w-4 h-4 mr-2" />
                  Export
                </Button>
                <div className="absolute right-0 mt-2 w-40 bg-white rounded-lg shadow-lg border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                  <button
                    onClick={() => handleExportChat('pdf')}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-t-lg"
                    data-testid="export-pdf"
                  >
                    Export as PDF
                  </button>
                  <button
                    onClick={() => handleExportChat('docx')}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    data-testid="export-docx"
                  >
                    Export as DOCX
                  </button>
                  <button
                    onClick={() => handleExportChat('txt')}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-b-lg"
                    data-testid="export-txt"
                  >
                    Export as TXT
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4" data-testid="messages-container">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center max-w-md">
                <Scale className="w-16 h-16 mx-auto mb-4" style={{ color: theme.primary }} />
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome to Pleader AI</h2>
                <p className="text-gray-600 mb-6">
                  Your personal legal assistant. Ask me anything about Indian law, or upload documents for analysis.
                </p>
                <div className="grid grid-cols-2 gap-2">
                  {quickPrompts.map((prompt, index) => (
                    <button
                      key={index}
                      onClick={() => setInputMessage(prompt)}
                      className="px-4 py-2 text-sm rounded-lg border"
                      style={{ backgroundColor: theme.background, color: theme.primaryDark, borderColor: theme.hover }}
                      data-testid={`quick-prompt-${index}`}
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in message-wrapper`}
                  data-testid={`message-${index}`}
                >
                  <div className={`flex space-x-3 max-w-3xl w-full ${message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                    <Avatar className="flex-shrink-0">
                      <AvatarFallback
                        className={message.sender === 'user' ? 'text-white' : 'bg-gradient-to-br from-gray-100 to-gray-200'}
                        style={message.sender === 'user' ? { background: `linear-gradient(to bottom right, ${theme.primary}, ${theme.primaryDark})` } : {}}
                      >
                        {message.sender === 'user' ? (
                          user?.name?.charAt(0).toUpperCase()
                        ) : (
                          <Scale className="w-5 h-5" style={{ color: theme.primaryDark }} />
                        )}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0">
                      <div
                        className={`rounded-2xl p-5 shadow-sm ${message.sender === 'user' ? 'text-white' : 'bg-white border border-gray-100'}`}
                        style={message.sender === 'user' ? { background: `linear-gradient(to bottom right, ${theme.primary}, ${theme.primaryDark})`, fontFamily: 'Inter, system-ui, sans-serif' } : { fontFamily: 'Inter, system-ui, sans-serif' }}
                      >
                        <div
                          className={`text-base leading-relaxed whitespace-pre-wrap ${message.sender === 'user' ? 'text-white' : 'text-gray-900'}`}
                          style={{ fontSize: '16px', lineHeight: '1.6' }}
                        >
                          {message.sender === 'user' ? (
                            message.content
                          ) : (
                            <ReactMarkdown
                              remarkPlugins={[remarkGfm]}
                              components={{
                                h1: ({ node, ...props }) => <h1 className="text-2xl font-bold mt-4 mb-2" {...props} />,
                                h2: ({ node, ...props }) => <h2 className="text-xl font-bold mt-4 mb-2" {...props} />,
                                h3: ({ node, ...props }) => <h3 className="text-lg font-bold mt-3 mb-1" {...props} />,
                                ul: ({ node, ...props }) => <ul className="list-disc ml-4 mb-2 space-y-1" {...props} />,
                                ol: ({ node, ...props }) => <ol className="list-decimal ml-4 mb-2 space-y-1" {...props} />,
                                li: ({ node, ...props }) => <li className="mb-1" {...props} />,
                                p: ({ node, ...props }) => <p className="mb-2 last:mb-0" {...props} />,
                                a: ({ node, ...props }) => <a className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer" {...props} />,
                                code: ({ node, ...props }) => <code className="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono text-red-500" {...props} />,
                                blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-gray-200 pl-4 py-1 italic text-gray-600 mb-2" {...props} />
                              }}
                            >
                              {message.content}
                            </ReactMarkdown>
                          )}
                        </div>
                        {message.timestamp && (
                          <p className="text-xs opacity-60 mt-2">
                            {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </p>
                        )}
                      </div>
                      {message.sender === 'ai' && (
                        <div className="flex items-center space-x-2 mt-2 message-actions">
                          <button
                            onClick={() => handleCopyMessage(message.content)}
                            className="p-1.5 hover:bg-gray-100 rounded-md transition-colors"
                            data-testid={`copy-message-${index}`}
                            title="Copy"
                          >
                            <Copy className="w-4 h-4 text-gray-500" />
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start animate-fade-in">
                  <div className="flex space-x-3 max-w-3xl">
                    <Avatar>
                      <AvatarFallback className="bg-gray-200">
                        <Scale className="w-5 h-5" style={{ color: theme.primaryDark }} />
                      </AvatarFallback>
                    </Avatar>
                    <div className="bg-white border border-gray-200 rounded-2xl p-4">
                      <div className="flex space-x-2">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="bg-transparent p-4 pb-6">
          <form onSubmit={handleSendMessage} className="max-w-3xl mx-auto">
            <div className="flex items-end space-x-3 bg-white p-2 rounded-3xl shadow-xl border border-gray-100">
              <div className="flex-1 relative">
                <Input
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Ask me anything about Indian law..."
                  className="h-12 pr-12 bg-transparent border-0 focus:ring-0 text-base shadow-none focus-visible:ring-0"
                  disabled={loading}
                  data-testid="message-input"
                />
                <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex space-x-1">
                  <VoiceInput
                    onTranscript={handleVoiceTranscript}
                    disabled={loading}
                  />
                </div>
              </div>
              <Button
                type="submit"
                disabled={!inputMessage.trim() || loading}
                className="h-10 w-10 p-0 rounded-full flex items-center justify-center transition-all hover:opacity-90 active:scale-95 text-white"
                style={{ background: theme.primary }}
                data-testid="send-button"
              >
                {loading ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </Button>
            </div>
            <div className="text-center mt-2">
              <p className="text-xs text-gray-400">Pleader AI can make mistakes. Verify important legal information.</p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
