import React, { useState, useEffect, useRef } from 'react';

export interface ChatWidgetProps {
  apiEndpoint: string;
  widgetId: string;
  theme?: 'light' | 'dark';
  primaryColor?: string;
  logoUrl?: string;
  greeting?: string;
  placeholder?: string;
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  size?: 'small' | 'medium' | 'large';
}

export interface WidgetMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations: string[];
  timestamp: number;
}

export const ChatWidget: React.FC<ChatWidgetProps> = ({
  apiEndpoint,
  widgetId,
  theme = 'dark',
  primaryColor = '#6366f1',
  logoUrl,
  greeting = 'Hello! How can I help you?',
  placeholder = 'Ask a question...',
  position = 'bottom-right',
  size = 'medium'
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<WidgetMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (messages.length === 0 && greeting) {
      setMessages([
        {
          id: 'greeting',
          role: 'assistant',
          content: greeting,
          citations: [],
          timestamp: Date.now()
        }
      ]);
    }
  }, [greeting, messages.length]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMessage: WidgetMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      citations: [],
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Production: replace with real fetch call
      const response = await fetch(`${apiEndpoint}/api/v1/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage.content, widgetId })
      });
      
      const data = await response.json();
      
      const assistantMessage: WidgetMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.content || 'This is a mock response.',
        citations: data.citations || [],
        timestamp: Date.now()
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: WidgetMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        citations: [],
        timestamp: Date.now()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const isDark = theme === 'dark';
  
  const positionStyles = {
    'bottom-right': { bottom: '20px', right: '20px' },
    'bottom-left': { bottom: '20px', left: '20px' },
    'top-right': { top: '20px', right: '20px' },
    'top-left': { top: '20px', left: '20px' }
  }[position];

  const sizeStyles = {
    small: { width: '300px', height: '400px' },
    medium: { width: '350px', height: '500px' },
    large: { width: '400px', height: '600px' }
  }[size];

  const containerStyle: React.CSSProperties = {
    position: 'fixed',
    ...positionStyles,
    zIndex: 9999,
    fontFamily: 'system-ui, -apple-system, sans-serif'
  };

  const fabStyle: React.CSSProperties = {
    width: '60px',
    height: '60px',
    borderRadius: '50%',
    backgroundColor: primaryColor,
    color: '#fff',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
    border: 'none',
    position: 'absolute',
    ...positionStyles
  };

  const panelStyle: React.CSSProperties = {
    ...sizeStyles,
    backgroundColor: isDark ? '#1f2937' : '#ffffff',
    color: isDark ? '#f3f4f6' : '#111827',
    borderRadius: '12px',
    boxShadow: '0 8px 24px rgba(0,0,0,0.2)',
    display: isOpen ? 'flex' : 'none',
    flexDirection: 'column',
    overflow: 'hidden',
    position: 'absolute',
    bottom: position.includes('bottom') ? '80px' : 'auto',
    top: position.includes('top') ? '80px' : 'auto',
    right: position.includes('right') ? '0' : 'auto',
    left: position.includes('left') ? '0' : 'auto'
  };

  const headerStyle: React.CSSProperties = {
    padding: '16px',
    backgroundColor: primaryColor,
    color: '#fff',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    fontWeight: 'bold'
  };

  const messagesStyle: React.CSSProperties = {
    flex: 1,
    overflowY: 'auto',
    padding: '16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px'
  };

  const inputContainerStyle: React.CSSProperties = {
    padding: '16px',
    borderTop: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`,
    display: 'flex',
    gap: '8px'
  };

  const inputStyle: React.CSSProperties = {
    flex: 1,
    padding: '8px 12px',
    borderRadius: '20px',
    border: `1px solid ${isDark ? '#4b5563' : '#d1d5db'}`,
    backgroundColor: isDark ? '#374151' : '#f9fafb',
    color: isDark ? '#f3f4f6' : '#111827',
    outline: 'none'
  };

  const sendButtonStyle: React.CSSProperties = {
    backgroundColor: primaryColor,
    color: '#fff',
    border: 'none',
    borderRadius: '50%',
    width: '36px',
    height: '36px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  };

  return (
    <div style={containerStyle}>
      {!isOpen && (
        <button style={fabStyle} onClick={() => setIsOpen(true)}>
          💬
        </button>
      )}

      <div style={panelStyle}>
        <div style={headerStyle}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {logoUrl && <img src={logoUrl} alt="Logo" style={{ width: '24px', height: '24px', borderRadius: '50%' }} />}
            <span>Chat Assistant</span>
          </div>
          <button 
            onClick={() => setIsOpen(false)}
            style={{ background: 'none', border: 'none', color: '#fff', cursor: 'pointer', fontSize: '18px' }}
          >
            ✕
          </button>
        </div>

        <div style={messagesStyle}>
          {messages.map((msg) => (
            <div 
              key={msg.id}
              style={{
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '80%'
              }}
            >
              <div style={{
                backgroundColor: msg.role === 'user' ? primaryColor : (isDark ? '#374151' : '#f3f4f6'),
                color: msg.role === 'user' ? '#fff' : (isDark ? '#f3f4f6' : '#111827'),
                padding: '10px 14px',
                borderRadius: '16px',
                borderBottomRightRadius: msg.role === 'user' ? '4px' : '16px',
                borderBottomLeftRadius: msg.role === 'assistant' ? '4px' : '16px'
              }}>
                {msg.content}
              </div>
              
              {msg.citations && msg.citations.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '6px' }}>
                  {msg.citations.map((cit, idx) => (
                    <span 
                      key={idx}
                      style={{
                        fontSize: '10px',
                        backgroundColor: isDark ? '#4b5563' : '#e5e7eb',
                        padding: '2px 6px',
                        borderRadius: '10px',
                        color: isDark ? '#d1d5db' : '#4b5563'
                      }}
                    >
                      {cit}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
          {isLoading && (
            <div style={{ alignSelf: 'flex-start', padding: '10px', color: isDark ? '#9ca3af' : '#6b7280' }}>
              Typing...
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div style={inputContainerStyle}>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder={placeholder}
            style={inputStyle}
          />
          <button style={sendButtonStyle} onClick={handleSend} disabled={isLoading}>
            ➤
          </button>
        </div>
      </div>
    </div>
  );
};
