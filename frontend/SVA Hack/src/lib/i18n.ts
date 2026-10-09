import { SupportedLang } from '../types';

export interface LangConfig {
  code: SupportedLang;
  label: string;
  ttsLang: string;
}

export const SUPPORTED_LANGS: LangConfig[] = [
  { code: 'en', label: 'English', ttsLang: 'en-IN' },
  { code: 'hi', label: 'हिन्दी', ttsLang: 'hi-IN' }
];

export const I18N_SCENE_TEMPLATES: Record<SupportedLang, {
  hookPrefix: string;
  situationPrefix: string;
  meaningPrefix: string;
  actionPrefix: string;
  outro: string;
}> = {
  en: {
    hookPrefix: "Stop spiraling. Here is what's really happening:",
    situationPrefix: "When the weight feels too heavy and noise is everywhere...",
    meaningPrefix: "Swami Vivekananda cut straight through this illusion:",
    actionPrefix: "Your 2-minute reset right now:",
    outro: "You have all the strength inside you. Take a breath and step forward."
  },
  hi: {
    hookPrefix: "घबराना बंद कीजिए। वास्तव में क्या हो रहा है, समझिए:",
    situationPrefix: "जब दबाव बहुत भारी लगे और दिमाग में केवल शोर हो...",
    meaningPrefix: "स्वामी विवेकानंद ने इस भ्रम को सीधे शब्दों में काटा था:",
    actionPrefix: "आपका 2 मिनट का अभ्यास अभी:",
    outro: "सारी शक्ति आपके ही भीतर है। एक गहरी सांस लें और आगे बढ़ें।"
  }
};
