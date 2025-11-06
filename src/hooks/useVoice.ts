/**
 * useVoice Hook - Easy voice announcements in components
 */
import { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { voiceService } from '../services/voiceService';

export const useVoice = () => {
  const { i18n } = useTranslation();
  const [isEnabled, setIsEnabled] = useState(true);
  const [isSpeaking, setIsSpeaking] = useState(false);

  // Get current language
  const currentLanguage = i18n.language;

  // Update speaking status
  useEffect(() => {
    const interval = setInterval(() => {
      setIsSpeaking(voiceService.isSpeaking());
    }, 100);

    return () => clearInterval(interval);
  }, []);

  /**
   * Announce queue number (bilingual or single language)
   */
  const announceQueueNumber = useCallback((queueNumber: number, bilingual: boolean = false) => {
    if (!isEnabled) return;

    if (bilingual) {
      voiceService.announceQueueNumberBilingual(queueNumber);
    } else if (currentLanguage === 'sn') {
      voiceService.announceQueueNumberShona(queueNumber);
    } else {
      voiceService.announceQueueNumberEnglish(queueNumber);
    }
  }, [currentLanguage, isEnabled]);

  /**
   * Announce service call
   */
  const announceServiceCall = useCallback((queueNumber: number, serviceArea: string) => {
    if (!isEnabled) return;
    voiceService.announceServiceCall(queueNumber, serviceArea, currentLanguage);
  }, [currentLanguage, isEnabled]);

  /**
   * Welcome announcement
   */
  const announceWelcome = useCallback(() => {
    if (!isEnabled) return;
    voiceService.announceWelcome(currentLanguage);
  }, [currentLanguage, isEnabled]);

  /**
   * Emergency announcement
   */
  const announceEmergency = useCallback(() => {
    if (!isEnabled) return;
    voiceService.announceEmergency(currentLanguage);
  }, [currentLanguage, isEnabled]);

  /**
   * Speak custom text
   */
  const speak = useCallback((text: string, lang?: string) => {
    if (!isEnabled) return;
    voiceService.speak(text, lang || currentLanguage);
  }, [currentLanguage, isEnabled]);

  /**
   * Stop speaking
   */
  const stop = useCallback(() => {
    voiceService.stop();
  }, []);

  /**
   * Toggle voice on/off
   */
  const toggleVoice = useCallback(() => {
    const newState = !isEnabled;
    setIsEnabled(newState);
    voiceService.setEnabled(newState);
  }, [isEnabled]);

  /**
   * Test voice
   */
  const testVoice = useCallback(() => {
    voiceService.testVoice(currentLanguage);
  }, [currentLanguage]);

  return {
    isEnabled,
    isSpeaking,
    currentLanguage,
    announceQueueNumber,
    announceServiceCall,
    announceWelcome,
    announceEmergency,
    speak,
    stop,
    toggleVoice,
    testVoice,
  };
};
