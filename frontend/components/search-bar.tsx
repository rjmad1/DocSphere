import React, { useState, useEffect, useRef } from 'react';

export interface SearchBarProps {
  apiEndpoint: string;
  tenantId: string;
  placeholder?: string;
  maxResults?: number;
  onResultSelect?: (result: SearchResultItem) => void;
}

export interface SearchResultItem {
  entityId: string;
  score: number;
  snippet: string;
  source: string;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  apiEndpoint,
  tenantId,
  placeholder = 'Search...',
  maxResults = 5,
  onResultSelect
}) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Debounced search
  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      setIsDropdownOpen(false);
      return;
    }

    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        // Production: replace with real fetch
        const response = await fetch(`${apiEndpoint}/api/v1/retrieval/search`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query, tenantId, limit: maxResults })
        });
        const data = await response.json();
        
        // Mock data structure fallback
        const mockResults: SearchResultItem[] = data.results || [
          { entityId: '1', score: 0.95, snippet: `Found result for "${query}" in docs.`, source: 'Documentation' },
          { entityId: '2', score: 0.82, snippet: `Another reference to "${query}".`, source: 'API Reference' }
        ];
        
        setResults(mockResults);
        setIsDropdownOpen(true);
        setSelectedIndex(-1);
      } catch (error) {
        console.error('Search failed:', error);
        setResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query, apiEndpoint, tenantId, maxResults]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isDropdownOpen) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => (prev < results.length - 1 ? prev + 1 : prev));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => (prev > 0 ? prev - 1 : prev));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (selectedIndex >= 0 && selectedIndex < results.length) {
        handleSelect(results[selectedIndex]);
      }
    } else if (e.key === 'Escape') {
      setIsDropdownOpen(false);
    }
  };

  const handleSelect = (result: SearchResultItem) => {
    if (onResultSelect) {
      onResultSelect(result);
    }
    setIsDropdownOpen(false);
    setQuery('');
  };

  const containerStyle: React.CSSProperties = {
    position: 'relative',
    width: '100%',
    maxWidth: '500px',
    fontFamily: 'system-ui, -apple-system, sans-serif'
  };

  const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '12px 16px',
    paddingRight: '40px',
    borderRadius: '8px',
    border: '1px solid #d1d5db',
    fontSize: '16px',
    outline: 'none',
    boxSizing: 'border-box',
    boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
  };

  const dropdownStyle: React.CSSProperties = {
    position: 'absolute',
    top: '100%',
    left: 0,
    right: 0,
    marginTop: '4px',
    backgroundColor: '#fff',
    borderRadius: '8px',
    boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06)',
    border: '1px solid #e5e7eb',
    zIndex: 50,
    maxHeight: '400px',
    overflowY: 'auto'
  };

  return (
    <div ref={containerRef} style={containerStyle}>
      <div style={{ position: 'relative' }}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => { if (results.length > 0) setIsDropdownOpen(true); }}
          placeholder={placeholder}
          style={inputStyle}
        />
        {isSearching && (
          <div style={{ position: 'absolute', right: '12px', top: '12px', color: '#9ca3af' }}>
            ...
          </div>
        )}
      </div>

      {isDropdownOpen && results.length > 0 && (
        <div style={dropdownStyle}>
          {results.map((result, idx) => (
            <div
              key={result.entityId}
              onClick={() => handleSelect(result)}
              onMouseEnter={() => setSelectedIndex(idx)}
              style={{
                padding: '12px 16px',
                cursor: 'pointer',
                backgroundColor: selectedIndex === idx ? '#f3f4f6' : '#fff',
                borderBottom: idx < results.length - 1 ? '1px solid #f3f4f6' : 'none'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span style={{ fontSize: '12px', fontWeight: 600, color: '#6366f1' }}>
                  {result.source}
                </span>
                <span style={{ fontSize: '12px', color: '#9ca3af' }}>
                  Score: {Math.round(result.score * 100)}%
                </span>
              </div>
              <div style={{ fontSize: '14px', color: '#374151', lineHeight: '1.4' }}>
                {result.snippet}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
