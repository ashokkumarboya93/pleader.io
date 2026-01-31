import React, { useState, useEffect } from 'react';
import { Mic, MicOff } from 'lucide-react';

export function VoiceInput({ onTranscript, disabled }) {
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const [interimTranscript, setInterimTranscript] = useState('');

  useEffect(() => {
    // Check if Web Speech API is supported
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      
      recognitionInstance.continuous = true;
      recognitionInstance.interimResults = true;
      recognitionInstance.lang = 'en-US';

      recognitionInstance.onresult = (event) => {
        let interim = '';
        let final = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            final += transcript + ' ';
          } else {
            interim += transcript;
          }
        }

        if (interim) {
          setInterimTranscript(interim);
        }

        if (final) {
          onTranscript(final.trim());
          setInterimTranscript('');
        }
      };

      recognitionInstance.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognitionInstance.onend = () => {
        setIsListening(false);
      };

      setRecognition(recognitionInstance);
    }

    return () => {
      if (recognition) {
        recognition.stop();
      }
    };
  }, []);

  const toggleListening = () => {
    if (!recognition) {
      alert('Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    if (isListening) {
      recognition.stop();
      setIsListening(false);
      setInterimTranscript('');
    } else {
      recognition.start();
      setIsListening(true);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={toggleListening}
        disabled={disabled}
        className={`
          p-2 rounded-lg transition-all duration-200
          ${
            isListening
              ? 'bg-red-500 text-white hover:bg-red-600 animate-pulse'
              : 'hover:bg-gray-100 text-gray-600'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}
        title={isListening ? 'Stop recording' : 'Start voice input'}
      >
        {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
      </button>

      {interimTranscript && (
        <div className="absolute bottom-full mb-2 right-0 bg-gray-900 text-white text-xs px-3 py-2 rounded-lg shadow-lg max-w-xs">
          <div className="font-medium mb-1">Listening...</div>
          <div className="opacity-75">{interimTranscript}</div>
        </div>
      )}
    </div>
  );
}
