import React, { useState } from 'react';
import { useTheme, THEMES } from '../context/ThemeContext';
import { Palette } from 'lucide-react';

export function ThemeSwitcher() {
  const { currentTheme, changeTheme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 rounded-lg hover:bg-gray-100 transition-all duration-200"
        title="Change Theme"
      >
        <Palette className="w-5 h-5 text-gray-600" />
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Theme selector */}
          <div className="absolute right-0 mt-2 p-4 bg-white rounded-lg shadow-xl border border-gray-200 z-50 min-w-[280px]">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Choose Theme</h3>
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(THEMES).map(([key, theme]) => (
                <button
                  key={key}
                  onClick={() => {
                    changeTheme(key);
                    setIsOpen(false);
                  }}
                  className={`
                    flex flex-col items-center p-3 rounded-lg border-2 transition-all duration-200
                    ${
                      currentTheme === key
                        ? 'border-gray-900 shadow-md'
                        : 'border-gray-200 hover:border-gray-300'
                    }
                  `}
                >
                  <div
                    className="w-12 h-12 rounded-full mb-2 transition-transform duration-200 hover:scale-110"
                    style={{ backgroundColor: theme.primary }}
                  />
                  <span className="text-xs font-medium text-gray-700">
                    {theme.name}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
