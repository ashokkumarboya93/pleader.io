import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const THEMES = {
  green: {
    name: 'Green',
    primary: '#4ADE80',
    primaryDark: '#22C55E',
    primaryLight: '#86EFAC',
    background: '#DCFCE7',
    hover: '#BBF7D0'
  },
  blue: {
    name: 'Blue',
    primary: '#60A5FA',
    primaryDark: '#3B82F6',
    primaryLight: '#93C5FD',
    background: '#DBEAFE',
    hover: '#BFDBFE'
  },
  purple: {
    name: 'Purple',
    primary: '#C084FC',
    primaryDark: '#A855F7',
    primaryLight: '#D8B4FE',
    background: '#F3E8FF',
    hover: '#E9D5FF'
  },
  orange: {
    name: 'Orange',
    primary: '#FB923C',
    primaryDark: '#F97316',
    primaryLight: '#FDBA74',
    background: '#FFEDD5',
    hover: '#FED7AA'
  },
  pink: {
    name: 'Pink',
    primary: '#F472B6',
    primaryDark: '#EC4899',
    primaryLight: '#F9A8D4',
    background: '#FCE7F3',
    hover: '#FBCFE8'
  },
  gray: {
    name: 'Gray',
    primary: '#9CA3AF',
    primaryDark: '#6B7280',
    primaryLight: '#D1D5DB',
    background: '#F3F4F6',
    hover: '#E5E7EB'
  }
};

export function ThemeProvider({ children }) {
  const [currentTheme, setCurrentTheme] = useState(() => {
    return localStorage.getItem('pleader-theme') || 'green';
  });

  useEffect(() => {
    const root = document.documentElement;
    const theme = THEMES[currentTheme];
    
    // Set CSS variables
    root.style.setProperty('--theme-primary', theme.primary);
    root.style.setProperty('--theme-primary-dark', theme.primaryDark);
    root.style.setProperty('--theme-primary-light', theme.primaryLight);
    root.style.setProperty('--theme-background', theme.background);
    root.style.setProperty('--theme-hover', theme.hover);
    
    // Save to localStorage
    localStorage.setItem('pleader-theme', currentTheme);
  }, [currentTheme]);

  const changeTheme = (themeName) => {
    if (THEMES[themeName]) {
      setCurrentTheme(themeName);
    }
  };

  return (
    <ThemeContext.Provider value={{ currentTheme, changeTheme, themes: THEMES }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
