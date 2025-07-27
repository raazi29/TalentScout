"""
Language Manager for TalentScout Hiring Assistant.

Handles multilingual support, language detection, and translation.
"""
import re
from typing import Dict, List, Optional, Tuple
import json
import os

class LanguageManager:
    """Manages multilingual support for the TalentScout chatbot."""
    
    # Supported languages with their codes and names
    SUPPORTED_LANGUAGES = {
        "en": {
            "name": "English",
            "native_name": "English",
            "flag": "🇺🇸"
        },
        "es": {
            "name": "Spanish",
            "native_name": "Español",
            "flag": "🇪🇸"
        },
        "fr": {
            "name": "French",
            "native_name": "Français",
            "flag": "🇫🇷"
        },
        "de": {
            "name": "German",
            "native_name": "Deutsch",
            "flag": "🇩🇪"
        },
        "it": {
            "name": "Italian",
            "native_name": "Italiano",
            "flag": "🇮🇹"
        },
        "pt": {
            "name": "Portuguese",
            "native_name": "Português",
            "flag": "🇵🇹"
        },
        "ru": {
            "name": "Russian",
            "native_name": "Русский",
            "flag": "🇷🇺"
        },
        "zh": {
            "name": "Chinese",
            "native_name": "中文",
            "flag": "🇨🇳"
        },
        "ja": {
            "name": "Japanese",
            "native_name": "日本語",
            "flag": "🇯🇵"
        },
        "ko": {
            "name": "Korean",
            "native_name": "한국어",
            "flag": "🇰🇷"
        },
        "hi": {
            "name": "Hindi",
            "native_name": "हिन्दी",
            "flag": "🇮🇳"
        },
        "bn": {
            "name": "Bengali",
            "native_name": "বাংলা",
            "flag": "🇮🇳"
        },
        "ta": {
            "name": "Tamil",
            "native_name": "தமிழ்",
            "flag": "🇮🇳"
        },
        "te": {
            "name": "Telugu",
            "native_name": "తెలుగు",
            "flag": "🇮🇳"
        },
        "mr": {
            "name": "Marathi",
            "native_name": "मराठी",
            "flag": "🇮🇳"
        },
        "gu": {
            "name": "Gujarati",
            "native_name": "ગુજરાતી",
            "flag": "🇮🇳"
        },
        "kn": {
            "name": "Kannada",
            "native_name": "ಕನ್ನಡ",
            "flag": "🇮🇳"
        },
        "ml": {
            "name": "Malayalam",
            "native_name": "മലയാളം",
            "flag": "🇮🇳"
        },
        "pa": {
            "name": "Punjabi",
            "native_name": "ਪੰਜਾਬੀ",
            "flag": "🇮🇳"
        },
        "ur": {
            "name": "Urdu",
            "native_name": "اردو",
            "flag": "🇮🇳"
        },
        "ar": {
            "name": "Arabic",
            "native_name": "العربية",
            "flag": "🇸🇦"
        }
    }
    
    # Language detection patterns
    LANGUAGE_PATTERNS = {
        "en": [
            r"\b(hello|hi|hey|good|morning|afternoon|evening|name|email|phone|experience|years|position|location|tech|stack|programming|language|framework|database|cloud|tool)\b",
            r"\b(thank|you|please|help|assist|interview|candidate|recruitment|job|career|skill|technology)\b"
        ],
        "es": [
            r"\b(hola|buenos|días|tardes|noches|nombre|correo|teléfono|experiencia|años|posición|ubicación|tecnología|programación|lenguaje|marco|base|datos|nube|herramienta)\b",
            r"\b(gracias|por|favor|ayuda|asistir|entrevista|candidato|reclutamiento|trabajo|carrera|habilidad)\b"
        ],
        "fr": [
            r"\b(bonjour|salut|bon|matin|après-midi|soir|nom|email|téléphone|expérience|années|poste|localisation|technologie|programmation|langage|cadre|base|données|nuage|outil)\b",
            r"\b(merci|s'il|vous|plaît|aider|assister|entretien|candidat|recrutement|travail|carrière|compétence)\b"
        ],
        "de": [
            r"\b(hallo|guten|morgen|tag|abend|name|email|telefon|erfahrung|jahre|position|standort|technologie|programmierung|sprache|rahmen|datenbank|wolke|werkzeug)\b",
            r"\b(danke|bitte|helfen|unterstützen|interview|kandidat|rekrutierung|arbeit|karriere|fähigkeit)\b"
        ],
        "it": [
            r"\b(ciao|buongiorno|buonasera|nome|email|telefono|esperienza|anni|posizione|località|tecnologia|programmazione|linguaggio|framework|database|cloud|strumento)\b",
            r"\b(grazie|per|favore|aiutare|assistere|intervista|candidato|reclutamento|lavoro|carriera|abilità)\b"
        ],
        "pt": [
            r"\b(olá|bom|dia|tarde|noite|nome|email|telefone|experiência|anos|posição|localização|tecnologia|programação|linguagem|framework|banco|dados|nuvem|ferramenta)\b",
            r"\b(obrigado|por|favor|ajudar|assistir|entrevista|candidato|recrutamento|trabalho|carreira|habilidade)\b"
        ],
        "ru": [
            r"\b(привет|здравствуйте|добрый|утро|день|вечер|имя|почта|телефон|опыт|годы|позиция|местоположение|технология|программирование|язык|фреймворк|база|данных|облако|инструмент)\b",
            r"\b(спасибо|пожалуйста|помочь|помощь|собеседование|кандидат|рекрутинг|работа|карьера|навык)\b"
        ],
        "zh": [
            r"\b(你好|早上好|下午好|晚上好|姓名|邮箱|电话|经验|年|职位|位置|技术|编程|语言|框架|数据库|云|工具)\b",
            r"\b(谢谢|请|帮助|协助|面试|候选人|招聘|工作|职业|技能)\b"
        ],
        "ja": [
            r"\b(こんにちは|おはよう|こんばんは|名前|メール|電話|経験|年|職位|場所|技術|プログラミング|言語|フレームワーク|データベース|クラウド|ツール)\b",
            r"\b(ありがとう|お願い|助ける|支援|面接|候補者|採用|仕事|キャリア|スキル)\b"
        ],
        "ko": [
            r"\b(안녕하세요|좋은|아침|오후|저녁|이름|이메일|전화|경험|년|직위|위치|기술|프로그래밍|언어|프레임워크|데이터베이스|클라우드|도구)\b",
            r"\b(감사합니다|부탁|도움|지원|면접|후보자|채용|일|경력|기술)\b"
        ],
        "hi": [
            r"\b(नमस्ते|सुप्रभात|शुभ|दोपहर|शाम|नाम|ईमेल|फोन|अनुभव|साल|पद|स्थान|तकनीक|प्रोग्रामिंग|भाषा|फ्रेमवर्क|डेटाबेस|क्लाउड|उपकरण)\b",
            r"\b(धन्यवाद|कृपया|मदद|सहायता|साक्षात्कार|उम्मीदवार|भर्ती|काम|करियर|कौशल)\b"
        ],
        "bn": [
            r"\b(নমস্কার|শুভ|সকাল|দুਪਹਿਰ|সাঁঁਜ|নাঁম|ইমেইল|ফোঁন|অভিজ্ঞতা|বছর|পদ|স্থান|প্রযুক্তি|প্রোগ্রামিং|ভাষা|ফ্রেমওয়ার্ক|ডাটাবেস|ক্লাউড|সরঞ্জাম)\b",
            r"\b(ধন্যবাদ|অনুগ্রহ|সাহায্য|সহায়তা|সাক্ষাৎকার|প্রার্থী|নিয়োগ|কাজ|ক্যারিয়ার|দক্ষতা)\b"
        ],
        "ta": [
            r"\b(வணக்கம்|காலை|மதியம்|மாலை|பெயர்|மின்னஞ்சல்|தொலைபேசி|அனுபவம்|ஆண்டுகள்|பதவி|இடம்|தொழில்நுட்பம்|நிரலாக்கம்|மொழி|கட்டமைப்பு|தரவுத்தளம்|மேகம்|கருவி|என்ன|உங்கள்|என்|நான்)\b",
            r"\b(நன்றி|தயவுசெய்து|உதவி|ஆதரவு|நேர்காணல்|விண்ணப்பதாரர்|மனிதவளம்|வேலை|வாழ்க்கை|திறமை|கேள்வி|பதில்)\b"
        ],
        "te": [
            r"\b(నమస్కారం|శుభోదయం|శుభ|మధ్యాహ్నం|సాయంత్రం|పేరు|ఇమెయిల్|ఫోన్|అనుభవం|సంవత్సరాలు|పదవి|స్థానం|టెక్నాలజీ|ప్రోగ్రామింగ్|భాష|ఫ్రేమ్‌వర్క్|డేటాబేస్|క్లౌడ్|సాధనం|ఏమిటి|మీ|నా|నేను)\b",
            r"\b(ధన్యవాదాలు|దయచేసి|సహాయం|మద్దతు|ఇంటర్వ్యూ|అభ్యర్థి|నియామకాతి|కెలస|వృత్తి|కౌశల్య|ప్రశ్న|సమాధానం)\b"
        ],
        "mr": [
            r"\b(नमस्कार|सुप्रभात|शुभ|दुपार|संध्याकाळ|नाव|ईमेल|फोन|अनुभव|वर्षे|पद|स्थान|तंत्रज्ञान|प्रोग्रामिंग|भाषा|फ्रेमवर्क|डेटाबेस|क्लाउड|साधन)\b",
            r"\b(धन्यवाद|कृपया|मदत|सहाय्य|मुलाखत|उमेदवार|भरती|काम|करिअर|कौशल्य)\b"
        ],
        "gu": [
            r"\b(નમસ્તે|સુપ્રભાત|શુભ|બપોર|સાંજ|નામ|ઈમેલ|ફોન|અનુભવ|વર્ષ|પદ|સ્થાન|ટેકનોલોજી|પ્રોગ્રામિંગ|ભાષા|ફ્રેમવર્ક|ડેટાબેસ|ક્લાઉડ|સાધન|શું|તમારું|મારું|હું)\b",
            r"\b(ધન્યવાદ|કૃપા|મદદ|સહાય|ઇન્ટરવ્યૂ|ઉમેદવાર|ભરતી|કામ|કારકિર્દી|કૌશલ્ય|પ્રશ્ન|જવાબ)\b"
        ],
        "kn": [
            r"\b(ನಮಸ್ಕಾರ|ಶುಭೋದಯ|ಶುಭ|ಮಧ್ಯಾಹ್ನ|ಸಂಜೆ|ಹೆಸರು|ಇಮೇಲ್|ಫೋನ್|ಅನುಭವ|ವರ್ಷಗಳು|ಹುದ್ದೆ|ಸ್ಥಳ|ತಂತ್ರಜ್ಞಾನ|ಪ್ರೋಗ್ರಾಮಿಂಗ್|ಭಾಷೆ|ಫ್ರೇಮ್‌ವರ್ಕ್|ಡೇಟಾಬೇಸ್|ಮೋಡ|ಉಪಕರಣ)\b",
            r"\b(ಧನ್ಯವಾದ|ದಯವಿಟ್ಟು|ಸಹಾಯ|ಬೆಂಬಲ|ಸಂದರ್ಶನ|ಅಭ್ಯರ್ಥಿ|ನೇಮಕಾತಿ|ಕೆಲಸ|ವೃತ್ತಿ|ಕೌಶಲ್ಯ)\b"
        ],
        "ml": [
            r"\b(നമസ്കാരം|സുപ്രഭാതം|ശുഭ|ഉച്ച|വൈകുന്നേരം|പേര്|ഇമെയിൽ|ഫോൺ|അനുഭവം|വർഷങ്ങൾ|സ്ഥാനം|സ്ഥലം|സാങ്കേതികവിദ്യ|പ്രോഗ്രാമിംഗ്|ഭാഷ|ഫ്രെയിംവർക്ക്|ഡാറ്റാബേസ്|മേഘം|ഉപകരണം|എന്താണ്|നിങ്ങളുടെ|എന്റെ|ഞാൻ)\b",
            r"\b(നന്ദി|ദയവായി|സഹായം|പിന്തുണ|ഇന്റർവ്യൂ|അഭ്യർത്ഥി|നിയമനം|ജോലി|കരിയർ|കഴിവ്|ചോദ്യം|ഉത്തരം)\b"
        ],
        "pa": [
            r"\b(ਸਤ ਸ੍ਰੀ ਅਕਾਲ|ਸ਼ੁਭ|ਸਵੇਰੇ|ਦੁਪਹਿਰ|ਸ਼ਾਮ|ਨਾਮ|ਈਮੇਲ|ਫੋਨ|ਅਨੁਭਵ|ਸਾਲ|ਪਦ|ਸਥਾਨ|ਟੈਕਨਾਲੋਜੀ|ਪ੍ਰੋਗਰਾਮਿੰਗ|ਭਾਸ਼ਾ|ਫਰੇਮਵਰਕ|ਡੇਟਾਬੇਸ|ਕਲਾਊਡ|ਸਾਧਨ)\b",
            r"\b(ਧੰਨਵਾਦ|ਕਿਰਪਾ|ਮਦਦ|ਸਹਾਇਤਾ|ਇੰਟਰਵਿਊ|ਉਮੀਦਵਾਰ|ਭਰਤੀ|ਕੰਮ|ਕਰੀਅਰ|ਕੌਸ਼ਲ)\b"
        ],
        "ur": [
            r"\b(السلام علیکم|صبح بخیر|شام بخیر|نام|ای میل|فون|تجربہ|سال|عہدہ|مقام|ٹیکنالوجی|پروگرامنگ|زبان|فریم ورک|ڈیٹا بیس|کلاؤڈ|آلہ)\b",
            r"\b(شکریہ|براہ کرم|مدد|حمایت|انٹرویو|امیدوار|بھرتی|کام|کیریئر|مہارت)\b"
        ],
        "ar": [
            r"\b(مرحبا|صباح|الخير|مساء|الخير|اسم|بريد|إلكتروني|هاتف|خبرة|سنوات|منصب|موقع|تقنية|برمجة|لغة|إطار|عمل|قاعدة|بيانات|سحابة|أداة)\b",
            r"\b(شكرا|من|فضلك|مساعدة|دعم|مقابلة|مرشح|توظيف|عمل|مهنة|مهارة)\b"
        ]
    }
    
    def __init__(self):
        """Initialize the language manager."""
        self.current_language = "en"
        self.detected_languages = {}
        self.language_preferences = {}
        
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Language code (e.g., 'en', 'es', 'fr')
        """
        text_lower = text.lower()
        language_scores = {}
        
        # Score each language based on pattern matches
        for lang_code, patterns in self.LANGUAGE_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                score += len(matches)
            language_scores[lang_code] = score
        
        # Find the language with the highest score
        if language_scores:
            detected_lang = max(language_scores, key=language_scores.get)
            if language_scores[detected_lang] > 0:
                return detected_lang
        
        # Default to English if no clear pattern is detected
        return "en"
    
    def set_language(self, language_code: str) -> bool:
        """
        Set the current language for the conversation.
        
        Args:
            language_code: Language code to set
            
        Returns:
            True if language is supported, False otherwise
        """
        if language_code in self.SUPPORTED_LANGUAGES:
            self.current_language = language_code
            return True
        return False
    
    def get_language_info(self, language_code: str) -> Optional[Dict]:
        """
        Get information about a specific language.
        
        Args:
            language_code: Language code
            
        Returns:
            Language information dictionary or None if not found
        """
        return self.SUPPORTED_LANGUAGES.get(language_code)
    
    def get_supported_languages(self) -> Dict:
        """
        Get all supported languages.
        
        Returns:
            Dictionary of supported languages
        """
        return self.SUPPORTED_LANGUAGES
    
    def translate_prompt(self, prompt: str, target_language: str) -> str:
        """
        Translate a prompt to the target language.
        
        Args:
            prompt: Original prompt in English
            target_language: Target language code
            
        Returns:
            Translated prompt
        """
        if target_language == "en":
            return prompt
        
        # Add translation instruction to the prompt
        translation_instruction = f"""
        Please translate the following text to {self.SUPPORTED_LANGUAGES[target_language]['name']} ({target_language}).
        Maintain the professional tone and technical accuracy of the original text.
        
        Original text:
        {prompt}
        
        Translation:
        """
        
        return translation_instruction
    
    def get_localized_greeting(self, language_code: str) -> str:
        """
        Get a localized greeting for the specified language.
        
        Args:
            language_code: Language code
            
        Returns:
            Localized greeting
        """
        greetings = {
            "en": "Hello! Welcome to TalentScout. I'm here to help you with your initial screening interview.",
            "es": "¡Hola! Bienvenido a TalentScout. Estoy aquí para ayudarte con tu entrevista de preselección inicial.",
            "fr": "Bonjour ! Bienvenue chez TalentScout. Je suis ici pour vous aider avec votre entretien de présélection initial.",
            "de": "Hallo! Willkommen bei TalentScout. Ich bin hier, um Ihnen bei Ihrem ersten Vorstellungsgespräch zu helfen.",
            "it": "Ciao! Benvenuto in TalentScout. Sono qui per aiutarti con la tua intervista di preselezione iniziale.",
            "pt": "Olá! Bem-vindo ao TalentScout. Estou aqui para ajudá-lo com sua entrevista de triagem inicial.",
            "ru": "Привет! Добро пожаловать в TalentScout. Я здесь, чтобы помочь вам с первоначальным собеседованием.",
            "zh": "你好！欢迎来到TalentScout。我在这里帮助您进行初步筛选面试。",
            "ja": "こんにちは！TalentScoutへようこそ。初回面接のお手伝いをさせていただきます。",
            "ko": "안녕하세요! TalentScout에 오신 것을 환영합니다. 초기 선별 면접을 도와드리겠습니다.",
            "hi": "नमस्ते! TalentScout में आपका स्वागत है। मैं आपकी प्रारंभिक स्क्रीनिंग साक्षात्कार में मदद करने के लिए यहां हूं।",
            "bn": "নমস্কার! TalentScout-এ স্বাগতম। আমি আপনার প্রাথমিক স্ক্রিনিং ইন্টারভিউতে সাহায্য করার জন্য এখানে আছি।",
            "ta": "வணக்கம்! TalentScout-க்கு வரவேற்கிறோம். நான் உங்கள் ஆரம்ப தேர்வு நேர்காணலில் உதவ இங்கே இருக்கிறேன்.",
            "te": "నమస్కారం! TalentScout కి స్వాగతం. నేను మీ ప్రారంభ స్క్రీనింగ్ ఇంటర్వ్యూలో సహాయం చేయడానికి ఇక్కడ ఉన్నాను.",
            "mr": "नमस्कार! TalentScout मध्ये आपले स्वागत आहे. मी तुमच्या प्रारंभिक स्क्रीनिंग मुलाखतीत मदत करण्यासाठी येथे आहे.",
            "gu": "નમસ્તે! TalentScout માં આપનું સ્વાગત છે. હું તમારી પ్રારંભિક સ్ક్રీનિંગ ઇન్ટરવ્યૂમાં મદદ કરવા માટે અહીં છું.",
            "kn": "ನಮಸ್ಕಾರ! TalentScout ಗೆ ಸುಸ್ವಾಗತ. ನಾನು ನಿಮ್ಮ ಆರಂಭಿಕ ಸ್ಕ್ರೀನಿಂಗ್ ಸಂದರ್ಶನದಲ್ಲಿ ಸಹಾಯ ಮಾಡಲು ಇಲ್ಲಿ ಇದ್ದೇನೆ.",
            "ml": "നമസ്കാരം! TalentScout-ലേക്ക് സ്വാഗതം. നിങ്ങളുടെ പ്രാരംഭ സ്ക്രീനിംഗ് ഇന്റർവ്യൂവിൽ സഹായിക്കാൻ ഞാൻ ഇവിടെയുണ്ട്.",
            "pa": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! TalentScout ਵਿੱਚ ਤੁਹਾਡਾ ਸਵਾਗਤ ਹੈ। ਮੈਂ ਤੁਹਾਡੀ ਸ਼ੁਰੂਆਤੀ ਸਕ੍ਰੀਨਿੰਗ ਇੰਟਰਵਿਊ ਵਿੱਚ ਮਦਦ ਕਰਨ ਲਈ ਇੱਥੇ ਹਾਂ।",
            "ur": "السلام علیکم! TalentScout میں آپ کا خیر مقدم ہے۔ میں آپ کی ابتدائی اسکریننگ انٹرویو میں مدد کرنے کے لیے یہاں ہوں۔",
            "ar": "مرحبا! أهلا وسهلا بك في TalentScout. أنا هنا لمساعدتك في مقابلة الفحص الأولي."
        }
        
        return greetings.get(language_code, greetings["en"])
    
    def get_language_selector_prompt(self) -> str:
        """
        Get a prompt for language selection.
        
        Returns:
            Language selection prompt
        """
        prompt = "Please select your preferred language for this interview:\n\n"
        
        for code, info in self.SUPPORTED_LANGUAGES.items():
            prompt += f"{info['flag']} {info['native_name']} ({info['name']}) - Type '{code}'\n"
        
        prompt += "\nOr simply start typing in your preferred language and I'll detect it automatically."
        
        return prompt
    
    def update_language_preference(self, session_id: str, language_code: str) -> None:
        """
        Update language preference for a specific session.
        
        Args:
            session_id: Session identifier
            language_code: Preferred language code
        """
        self.language_preferences[session_id] = language_code
    
    def get_session_language(self, session_id: str) -> str:
        """
        Get the preferred language for a specific session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Language code for the session
        """
        return self.language_preferences.get(session_id, "en") 