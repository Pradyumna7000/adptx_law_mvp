import React, { useState, useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Send, Loader2, ArrowLeft, Plus, MessageSquare, User, Bot, FileText, X, Upload } from 'lucide-react'
import { api } from '../utils/util'

const ChatPage = () => {
  const [chats, setChats] = useState([
    { id: 1, title: "Chat 1", messages: [] }
  ]);
  const [currentChatId, setCurrentChatId] = useState(1);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [pdfFile, setPdfFile] = useState(null);
  const [pdfPreview, setPdfPreview] = useState(null);
  const [showSidebar, setShowSidebar] = useState(false);
  const messagesEndRef = useRef(null)
  const fileInputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const startNewChat = () => {
    const newChatId = chats.length + 1;
    const newChat = {
      id: newChatId,
      title: `Chat ${newChatId}`,
      messages: []
    };
    setChats(prev => [...prev, newChat]);
    setCurrentChatId(newChatId);
    setInput('');
    setPdfFile(null);
    setPdfPreview(null);
  }

  const getCurrentChat = () => {
    return chats.find(chat => chat.id === currentChatId) || chats[0];
  }

  const getCurrentMessages = () => {
    return getCurrentChat().messages;
  }

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      setPdfFile(file);
      
      // Create preview URL
      const reader = new FileReader();
      reader.onload = (e) => {
        setPdfPreview(e.target.result);
      };
      reader.readAsDataURL(file);
    } else {
      alert('Please select a valid PDF file');
    }
  };

  const removePdfFile = () => {
    setPdfFile(null);
    setPdfPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  useEffect(() => {
    scrollToBottom()
  }, [chats, currentChatId])

  const handleSubmit = async (e) => {
    e.preventDefault();
    if ((!input.trim() && !pdfFile) || isLoading) return;

    const messageText = input.trim();
    
    // Create user message
    const userMessage = {
      id: `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      text: messageText || (pdfFile ? `Analyzing PDF: ${pdfFile.name}` : ''),
      sender: 'user',
      timestamp: new Date(),
      hasPdf: !!pdfFile
    };

    // Clear input immediately
    setInput('');
    
    // Update chat with user message
    setChats(prevChats => 
      prevChats.map(chat => 
        chat.id === currentChatId 
          ? { ...chat, messages: [...chat.messages, userMessage] }
          : chat
      )
    );
    
    setIsLoading(true);

    try {
      let response;
      let data;

      if (pdfFile) {
        // Use the analyze-pdf endpoint for PDF files
        const formData = new FormData();
        formData.append('file', pdfFile);
        formData.append('message', messageText || 'Please analyze this PDF document');
        formData.append('user_id', 'user123');
        
        response = await api.analyzePdf(file);
      } else {
        // Use the chat endpoint for text messages
        const requestBody = JSON.stringify({
          message: messageText,
          user_id: 'user123'
        });

        response = await api.chat(messageText);
      }

      data = response;
      
      // Create AI response message
      const aiMessage = {
        id: `ai_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        text: pdfFile ? (data.analysis || data.message || 'No response from the AI.') : (data.data || 'No response from the AI.'),
        sender: 'ai',
        timestamp: new Date(),
        executionTime: data.execution_time
      };
      
      // Add AI response to chat
      setChats(prevChats => 
        prevChats.map(chat => 
          chat.id === currentChatId 
            ? { ...chat, messages: [...chat.messages, aiMessage] }
            : chat
        )
      );

      // Clear PDF after successful processing
      if (pdfFile) {
        setPdfFile(null);
        setPdfPreview(null);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      }
      
    } catch (error) {
      console.error('Error:', error);
      
      // Create error message
      const errorMessage = {
        id: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        text: 'Sorry, there was an error processing your request. Please try again.',
        sender: 'ai',
        timestamp: new Date(),
        isError: true
      };
      
      setChats(prevChats => 
        prevChats.map(chat => 
          chat.id === currentChatId 
            ? { ...chat, messages: [...chat.messages, errorMessage] }
            : chat
        )
      );
    } finally {
      setIsLoading(false);
    }
  }

  const formatMessage = (text) => {
    // Convert markdown-style formatting to HTML
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code class="bg-gray-700 px-1 py-0.5 rounded text-sm">$1</code>')
      .replace(/\n/g, '<br>')
      .replace(/^# (.*$)/gim, '<h1 class="text-xl font-bold mb-2">$1</h1>')
      .replace(/^## (.*$)/gim, '<h2 class="text-lg font-semibold mb-2">$1</h2>')
      .replace(/^### (.*$)/gim, '<h3 class="text-md font-medium mb-1">$1</h3>')
      .replace(/^- (.*$)/gim, '<li class="ml-4">$1</li>')
      .replace(/^\d+\. (.*$)/gim, '<li class="ml-4">$1</li>');
  }

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  return (
    <div className="h-screen bg-adptx-dark-950 flex">
      {/* Sidebar - Chat List */}
      <div className="hidden md:flex w-80 bg-adptx-dark-900 border-r border-adptx-dark-800 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-adptx-dark-800">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <img src="/public/logo_without_bg.png" alt="adptx" className="h-6 w-auto" />
              <span className="ml-2 text-lg font-bold gradient-text">adptx</span>
            </div>
            <Link
              to="/"
              className="text-gray-400 hover:text-white transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
            </Link>
          </div>
          
          {/* New Chat Button */}
          <button
            onClick={startNewChat}
            className="w-full bg-gradient-to-r from-adptx-500 to-adptx-600 hover:from-adptx-600 hover:to-adptx-700 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-300 flex items-center justify-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>New Chat</span>
          </button>
        </div>

        {/* Chat List */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="space-y-2">
            {chats.map((chat) => (
              <button
                key={chat.id}
                onClick={() => setCurrentChatId(chat.id)}
                className={`w-full text-left p-3 rounded-lg transition-colors flex items-center space-x-3 ${
                  chat.id === currentChatId
                    ? 'bg-adptx-500/20 border border-adptx-500/30 text-adptx-500'
                    : 'bg-adptx-dark-800 hover:bg-adptx-dark-700 text-gray-300'
                }`}
              >
                <MessageSquare className="w-4 h-4" />
                <span className="text-sm truncate">{chat.title}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Mobile Sidebar Overlay */}
      {showSidebar && (
        <div className="md:hidden fixed inset-0 z-50">
          {/* Backdrop */}
          <div 
            className="absolute inset-0 bg-black bg-opacity-50"
            onClick={() => setShowSidebar(false)}
          />
          {/* Sidebar */}
          <div className="absolute left-0 top-0 h-full w-80 bg-adptx-dark-900 border-r border-adptx-dark-800 flex flex-col">
            {/* Header */}
            <div className="p-4 border-b border-adptx-dark-800">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <img src="/public/logo_without_bg.png" alt="adptx" className="h-6 w-auto" />
                  <span className="ml-2 text-lg font-bold gradient-text">adptx</span>
                </div>
                <button
                  onClick={() => setShowSidebar(false)}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              
              {/* New Chat Button */}
              <button
                onClick={() => {
                  startNewChat();
                  setShowSidebar(false);
                }}
                className="w-full bg-gradient-to-r from-adptx-500 to-adptx-600 hover:from-adptx-600 hover:to-adptx-700 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-300 flex items-center justify-center space-x-2"
              >
                <Plus className="w-4 h-4" />
                <span>New Chat</span>
              </button>
            </div>

            {/* Chat List */}
            <div className="flex-1 overflow-y-auto p-4">
              <div className="space-y-2">
                {chats.map((chat) => (
                  <button
                    key={chat.id}
                    onClick={() => {
                      setCurrentChatId(chat.id);
                      setShowSidebar(false);
                    }}
                    className={`w-full text-left p-3 rounded-lg transition-colors flex items-center space-x-3 ${
                      chat.id === currentChatId
                        ? 'bg-adptx-500/20 border border-adptx-500/30 text-adptx-500'
                        : 'bg-adptx-dark-800 hover:bg-adptx-dark-700 text-gray-300'
                    }`}
                  >
                    <MessageSquare className="w-4 h-4" />
                    <span className="text-sm truncate">{chat.title}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-adptx-dark-900 border-b border-adptx-dark-800 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {/* Mobile Menu Button */}
              <button
                onClick={() => setShowSidebar(!showSidebar)}
                className="md:hidden p-2 bg-adptx-dark-800 rounded-lg hover:bg-adptx-dark-700 transition-colors"
              >
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <div>
                <h1 className="text-lg md:text-xl font-semibold">AI Legal Assistant</h1>
                <p className="text-xs md:text-sm text-gray-400">Powered by adptx</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-xs md:text-sm text-gray-400">Online</span>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-3 md:p-4 space-y-3 md:space-y-4">
          {getCurrentMessages().length === 0 && (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-adptx-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <Bot className="w-8 h-8 text-adptx-500" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Welcome to adptx</h3>
              <p className="text-gray-400 mb-6">
                Ask me anything about Indian law, legal research, or get help with legal analysis.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 md:gap-4 max-w-2xl mx-auto">
                <button 
                  onClick={() => setInput("What are the fundamental rights in Indian Constitution?")}
                  className="p-4 bg-adptx-dark-800 rounded-lg hover:bg-adptx-dark-700 transition-colors text-left"
                >
                  <MessageSquare className="w-5 h-5 text-adptx-500 mb-2" />
                  <h4 className="font-medium text-sm">Constitutional Law</h4>
                  <p className="text-xs text-gray-400">Fundamental rights and duties</p>
                </button>
                <button 
                  onClick={() => setInput("Explain the Indian Contract Act")}
                  className="p-4 bg-adptx-dark-800 rounded-lg hover:bg-adptx-dark-700 transition-colors text-left"
                >
                  <MessageSquare className="w-5 h-5 text-adptx-500 mb-2" />
                  <h4 className="font-medium text-sm">Contract Law</h4>
                  <p className="text-xs text-gray-400">Contract formation and enforcement</p>
                </button>
                <button 
                  onClick={() => setInput("What are the remedies for breach of contract?")}
                  className="p-4 bg-adptx-dark-800 rounded-lg hover:bg-adptx-dark-700 transition-colors text-left"
                >
                  <MessageSquare className="w-5 h-5 text-adptx-500 mb-2" />
                  <h4 className="font-medium text-sm">Legal Remedies</h4>
                  <p className="text-xs text-gray-400">Contract breach and remedies</p>
                </button>
              </div>
            </div>
          )}

          {getCurrentMessages().map((message) => (
            <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`flex items-start space-x-3 max-w-3xl ${message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.sender === 'user' 
                    ? 'bg-gradient-to-r from-adptx-orange-500 to-adptx-orange-600' 
                    : 'bg-gradient-to-r from-adptx-500 to-adptx-600'
                }`}>
                  {message.sender === 'user' ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-white" />}
                </div>
                <div className={`rounded-lg px-4 py-3 ${
                  message.sender === 'user'
                    ? 'bg-gradient-to-r from-adptx-orange-500 to-adptx-orange-600 text-white'
                    : message.isError
                    ? 'bg-red-500/20 border border-red-500/30 text-red-200'
                    : 'bg-adptx-dark-800 text-gray-100'
                }`}>
                  {/* PDF Badge for user messages */}
                  {message.hasPdf && message.sender === 'user' && (
                    <div className="inline-flex items-center space-x-1 mb-2 px-2 py-1 rounded text-xs bg-adptx-orange-400/20 border border-adptx-orange-400/30">
                      <FileText className="w-3 h-3" />
                      <span>PDF attached</span>
                    </div>
                  )}
                  
                  {/* Execution Time Badge */}
                  {message.executionTime && message.sender === 'ai' && (
                    <div className="inline-flex items-center space-x-1 mb-2 px-2 py-1 rounded text-xs text-gray-400 bg-adptx-dark-700">
                      <span>Response time: {message.executionTime.toFixed(1)}s</span>
                    </div>
                  )}
                  
                  <div 
                    className="prose prose-invert max-w-none"
                    dangerouslySetInnerHTML={{ __html: formatMessage(message.text) }}
                  />
                  
                  <div className={`text-xs mt-2 ${message.sender === 'user' ? 'text-orange-100' : 'text-gray-400'}`}>
                    {formatTime(message.timestamp)}
                  </div>
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="flex items-start space-x-3 max-w-3xl">
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-adptx-500 to-adptx-600 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="bg-adptx-dark-800 rounded-lg px-4 py-3">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-adptx-500 rounded-full animate-pulse"></div>
                      <div className="w-2 h-2 bg-adptx-500 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
                      <div className="w-2 h-2 bg-adptx-500 rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
                    </div>
                    <span className="text-sm text-gray-400">
                      AI is thinking...
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* PDF Preview Area - Above Input */}
        {pdfFile && (
          <div className="bg-adptx-dark-800 border-t border-adptx-dark-700 p-3 md:p-4">
            <div className="flex items-center justify-between mb-2 md:mb-3">
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4 md:w-5 md:h-5 text-adptx-500" />
                <span className="text-xs md:text-sm font-medium text-gray-200">PDF Document Ready</span>
              </div>
              <button
                onClick={removePdfFile}
                className="text-gray-400 hover:text-red-400 transition-colors p-1"
              >
                <X className="w-3 h-3 md:w-4 md:h-4" />
              </button>
            </div>
            <div className="flex items-center space-x-2 md:space-x-3">
              <div className="flex-1 min-w-0">
                <p className="text-xs md:text-sm text-gray-300 truncate">{pdfFile.name}</p>
                <p className="text-xs text-gray-400">{(pdfFile.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
              <div className="w-12 h-16 md:w-16 md:h-20 bg-adptx-dark-700 rounded border border-adptx-dark-600 flex items-center justify-center flex-shrink-0">
                <FileText className="w-6 h-6 md:w-8 md:h-8 text-adptx-500" />
              </div>
            </div>
          </div>
        )}

        {/* Input Area */}
        <form onSubmit={handleSubmit} className="flex items-center p-3 md:p-4 border-t border-adptx-dark-800 bg-adptx-dark-900">
          {/* File Upload Button */}
          <div className="mr-2 md:mr-3">
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileUpload}
              className="hidden"
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="p-2 md:p-3 bg-adptx-dark-800 hover:bg-adptx-dark-700 border border-adptx-dark-700 hover:border-adptx-500 rounded-full transition-all duration-200"
              title="Upload PDF"
            >
              <Upload className="h-4 w-4 md:h-5 md:w-5 text-gray-400 hover:text-adptx-500" />
            </button>
          </div>
          
          <div className="relative flex-1">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={pdfFile ? "Ask a question about the PDF..." : "Type your message..."}
              className="w-full px-3 md:px-4 py-2 md:py-3 border border-adptx-dark-700 rounded-full focus:outline-none focus:ring-2 focus:ring-adptx-500 focus:border-transparent bg-adptx-dark-800 text-white placeholder-gray-400 text-sm md:text-base"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
            />
          </div>
          <button
            type="submit"
            disabled={isLoading || (!input.trim() && !pdfFile)}
            className="ml-2 md:ml-3 p-2 md:p-3 bg-gradient-to-r from-adptx-500 to-adptx-600 hover:from-adptx-600 hover:to-adptx-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-full transition-all duration-200 transform hover:scale-105"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 md:h-5 md:w-5 text-white animate-spin" />
            ) : (
              <Send className="h-4 w-4 md:h-5 md:w-5 text-white" />
            )}
          </button>
        </form>
      </div>
    </div>
  )
}

export default ChatPage