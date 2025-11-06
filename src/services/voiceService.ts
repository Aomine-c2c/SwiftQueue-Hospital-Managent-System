/**
 * Voice Service - Text-to-Speech for Shona and English
 * Handles queue announcements and notifications
 */

interface VoiceConfig {
  lang: string;
  pitch: number;
  rate: number;
  volume: number;
}

class VoiceService {
  private synthesis: SpeechSynthesis | null = null;
  private voices: SpeechSynthesisVoice[] = [];
  private isEnabled: boolean = true;

  constructor() {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      this.synthesis = window.speechSynthesis;
      this.loadVoices();
      
      // Reload voices when they change (browser compatibility)
      if (this.synthesis) {
        this.synthesis.onvoiceschanged = () => {
          this.loadVoices();
        };
      }
    } else {
      console.warn('Text-to-Speech not supported in this browser');
      this.isEnabled = false;
    }
  }

  private loadVoices(): void {
    if (this.synthesis) {
      this.voices = this.synthesis.getVoices();
    }
  }

  /**
   * Get the best available voice for a language
   */
  private getVoiceForLanguage(lang: string): SpeechSynthesisVoice | null {
    if (this.voices.length === 0) {
      this.loadVoices();
    }

    // Try to find exact language match
    let voice = this.voices.find(v => v.lang === lang);
    
    // Fallback to language code (e.g., 'en' for 'en-US')
    if (!voice) {
      const langCode = lang.split('-')[0];
      voice = this.voices.find(v => v.lang.startsWith(langCode));
    }

    // For Shona, fallback to any available voice (browser may not have Shona)
    if (!voice && lang.includes('sn')) {
      // Use default voice
      voice = this.voices.find(v => v.default) || this.voices[0];
    }

    return voice || null;
  }

  /**
   * Speak text in specified language
   */
  speak(text: string, lang: string = 'en-US', config?: Partial<VoiceConfig>): void {
    if (!this.isEnabled || !this.synthesis || !text) {
      return;
    }

    // Cancel any ongoing speech
    this.synthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    
    // Set language
    utterance.lang = lang;

    // Find appropriate voice
    const voice = this.getVoiceForLanguage(lang);
    if (voice) {
      utterance.voice = voice;
    }

    // Apply configuration
    utterance.pitch = config?.pitch ?? 1;
    utterance.rate = config?.rate ?? 1;
    utterance.volume = config?.volume ?? 1;

    // Error handling
    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event);
    };

    // Speak
    this.synthesis.speak(utterance);
  }

  /**
   * Announce queue number in Shona
   */
  announceQueueNumberShona(queueNumber: number): void {
    const text = `Nhamba ${queueNumber}, tapota uyai kuchipatala`;
    this.speak(text, 'sn-ZW', { rate: 0.9 });
  }

  /**
   * Announce queue number in English
   */
  announceQueueNumberEnglish(queueNumber: number): void {
    const text = `Number ${queueNumber}, please proceed to the clinic`;
    this.speak(text, 'en-US', { rate: 0.9 });
  }

  /**
   * Bilingual queue announcement (Shona + English)
   */
  announceQueueNumberBilingual(queueNumber: number): void {
    // Announce in Shona first
    this.announceQueueNumberShona(queueNumber);
    
    // Then English after a pause
    setTimeout(() => {
      this.announceQueueNumberEnglish(queueNumber);
    }, 3000);
  }

  /**
   * Announce patient called to service area
   */
  announceServiceCall(queueNumber: number, serviceArea: string, language: string = 'en'): void {
    if (language === 'sn') {
      const text = `Nhamba ${queueNumber}, tapota uyai ku ${serviceArea}`;
      this.speak(text, 'sn-ZW', { rate: 0.9 });
    } else {
      const text = `Number ${queueNumber}, please proceed to ${serviceArea}`;
      this.speak(text, 'en-US', { rate: 0.9 });
    }
  }

  /**
   * Welcome message
   */
  announceWelcome(language: string = 'en'): void {
    if (language === 'sn') {
      this.speak('Mauya. Tapota tandara nhamba yenyu', 'sn-ZW');
    } else {
      this.speak('Welcome to SwiftQueue. Please register your number', 'en-US');
    }
  }

  /**
   * Emergency announcement
   */
  announceEmergency(language: string = 'en'): void {
    if (language === 'sn') {
      this.speak('Dambudziko! Tapota enda kune emergency', 'sn-ZW', { rate: 1.1, pitch: 1.2 });
    } else {
      this.speak('Emergency! Please proceed to the emergency department', 'en-US', { rate: 1.1, pitch: 1.2 });
    }
  }

  /**
   * Stop current speech
   */
  stop(): void {
    if (this.synthesis) {
      this.synthesis.cancel();
    }
  }

  /**
   * Pause speech
   */
  pause(): void {
    if (this.synthesis) {
      this.synthesis.pause();
    }
  }

  /**
   * Resume paused speech
   */
  resume(): void {
    if (this.synthesis) {
      this.synthesis.resume();
    }
  }

  /**
   * Check if speaking
   */
  isSpeaking(): boolean {
    return this.synthesis?.speaking || false;
  }

  /**
   * Enable/disable voice service
   */
  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
    if (!enabled) {
      this.stop();
    }
  }

  /**
   * Get available voices
   */
  getAvailableVoices(): SpeechSynthesisVoice[] {
    return this.voices;
  }

  /**
   * Test voice with sample text
   */
  testVoice(language: string = 'en'): void {
    if (language === 'sn') {
      this.speak('Mhoro, ndini voice yekuShona', 'sn-ZW');
    } else {
      this.speak('Hello, this is the English voice', 'en-US');
    }
  }
}

// Export singleton instance
export const voiceService = new VoiceService();
export default voiceService;
