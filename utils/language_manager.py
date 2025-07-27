"""
Language Manager for TalentScout Hiring Assistant.

Handles multilingual support, language detection, and translation.
"""
import re
from typing import Dict, List, Optional, Tuple, Any
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
        # Use the enhanced detection method but return only the language code for backward compatibility
        language, _ = self.detect_language_with_confidence(text)
        return language
    
    def detect_language_with_confidence(self, text: str) -> Tuple[str, float]:
        """
        Detect the language of the input text with confidence scoring.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Tuple of (language_code, confidence_score) where confidence is between 0.0 and 1.0
        """
        if not text or not text.strip():
            return "en", 0.0
            
        text_lower = text.lower().strip()
        text_length = len(text_lower.split())
        
        # If text is too short, confidence will be lower
        length_factor = min(1.0, text_length / 5.0)  # Full confidence at 5+ words
        
        language_scores = {}
        total_matches = 0
        
        # Score each language based on pattern matches
        for lang_code, patterns in self.LANGUAGE_PATTERNS.items():
            score = 0
            unique_matches = set()
            
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                # Count unique matches to avoid over-scoring repeated words
                for match in matches:
                    unique_matches.add(match)
            
            score = len(unique_matches)
            language_scores[lang_code] = score
            total_matches += score
        
        if not language_scores or total_matches == 0:
            return "en", 0.0
        
        # Find the language with the highest score
        detected_lang = max(language_scores, key=language_scores.get)
        max_score = language_scores[detected_lang]
        
        if max_score == 0:
            return "en", 0.0
        
        # Calculate confidence based on:
        # 1. Ratio of max score to total matches (dominance)
        # 2. Absolute score (strength of detection)
        # 3. Text length factor
        dominance_factor = max_score / total_matches if total_matches > 0 else 0
        strength_factor = min(1.0, max_score / 3.0)  # Full strength at 3+ unique matches
        
        # Combine factors for final confidence
        confidence = dominance_factor * strength_factor * length_factor
        
        # Apply minimum confidence threshold
        if confidence < 0.1:
            return "en", 0.0
        
        return detected_lang, min(1.0, confidence)
    
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
    
    def auto_switch_language(self, text: str, current_language: str, session_id: str = None) -> Tuple[str, bool, str]:
        """
        Automatically switch language based on user input with confidence thresholds.
        
        Args:
            text: User input text to analyze
            current_language: Current conversation language
            session_id: Optional session ID for preference tracking
            
        Returns:
            Tuple of (new_language, switched, message) where:
            - new_language: The language to use (may be same as current)
            - switched: Boolean indicating if language was switched
            - message: Optional message to show user about language change
        """
        if not text or not text.strip():
            return current_language, False, ""
        
        # Detect language with confidence
        detected_language, confidence = self.detect_language_with_confidence(text)
        
        # If detected language is the same as current, no switch needed
        if detected_language == current_language:
            return current_language, False, ""
        
        # High confidence threshold - automatic switch
        if confidence >= 0.7:
            if session_id:
                self.update_language_preference(session_id, detected_language)
            
            lang_info = self.get_language_info(detected_language)
            lang_name = lang_info['native_name'] if lang_info else detected_language
            
            message = f"🌍 Language automatically switched to {lang_name} (confidence: {confidence:.1%})"
            return detected_language, True, message
        
        # Medium confidence threshold - ask for confirmation
        elif confidence >= 0.5:
            lang_info = self.get_language_info(detected_language)
            lang_name = lang_info['native_name'] if lang_info else detected_language
            
            message = f"🤔 I detected you might be speaking {lang_name}. Would you like to switch to this language? (confidence: {confidence:.1%})"
            return current_language, False, message
        
        # Low confidence - stay with current language
        else:
            return current_language, False, ""
    
    def confirm_language_switch(self, target_language: str, session_id: str = None) -> Tuple[str, str]:
        """
        Confirm and execute a language switch.
        
        Args:
            target_language: Language to switch to
            session_id: Optional session ID for preference tracking
            
        Returns:
            Tuple of (new_language, confirmation_message)
        """
        if target_language not in self.SUPPORTED_LANGUAGES:
            return self.current_language, f"❌ Language '{target_language}' is not supported."
        
        # Update preferences
        if session_id:
            self.update_language_preference(session_id, target_language)
        
        self.current_language = target_language
        
        lang_info = self.get_language_info(target_language)
        lang_name = lang_info['native_name'] if lang_info else target_language
        
        # Get localized confirmation message
        confirmation_message = self.get_localized_greeting(target_language)
        
        return target_language, f"✅ Language switched to {lang_name}!\n\n{confirmation_message}"
    
    def get_language_switch_suggestions(self, text: str, current_language: str) -> List[Tuple[str, float]]:
        """
        Get language switch suggestions based on input text.
        
        Args:
            text: Input text to analyze
            current_language: Current conversation language
            
        Returns:
            List of (language_code, confidence) tuples sorted by confidence
        """
        if not text or not text.strip():
            return []
        
        text_lower = text.lower().strip()
        language_scores = {}
        
        # Score each language based on pattern matches
        for lang_code, patterns in self.LANGUAGE_PATTERNS.items():
            if lang_code == current_language:
                continue  # Skip current language
                
            score = 0
            unique_matches = set()
            
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    unique_matches.add(match)
            
            if unique_matches:
                # Calculate basic confidence
                text_length = len(text_lower.split())
                length_factor = min(1.0, text_length / 5.0)
                strength_factor = min(1.0, len(unique_matches) / 3.0)
                confidence = strength_factor * length_factor
                
                if confidence > 0.1:  # Only include meaningful suggestions
                    language_scores[lang_code] = confidence
        
        # Sort by confidence descending
        suggestions = sorted(language_scores.items(), key=lambda x: x[1], reverse=True)
        return suggestions[:3]  # Return top 3 suggestions
    
    def get_cultural_context(self, language: str) -> Dict[str, Any]:
        """
        Get cultural context information for a specific language.
        
        Args:
            language: Language code
            
        Returns:
            Dictionary containing cultural context information
        """
        cultural_contexts = {
            "en": {
                "greeting_style": "casual_professional",
                "formality_level": "medium",
                "name_format": "first_last",
                "phone_format": "+1-XXX-XXX-XXXX",
                "date_format": "MM/DD/YYYY",
                "time_format": "12_hour",
                "currency": "USD",
                "professional_titles": ["Mr.", "Ms.", "Dr.", "Prof."],
                "communication_style": "direct",
                "interview_expectations": "punctual, prepared, confident"
            },
            "es": {
                "greeting_style": "warm_professional",
                "formality_level": "high",
                "name_format": "first_paternal_maternal",
                "phone_format": "+XX-XXX-XXX-XXXX",
                "date_format": "DD/MM/YYYY",
                "time_format": "24_hour",
                "currency": "EUR/USD/local",
                "professional_titles": ["Sr.", "Sra.", "Dr.", "Ing."],
                "communication_style": "relationship_focused",
                "interview_expectations": "respectful, family_context_ok, relationship_building"
            },
            "fr": {
                "greeting_style": "formal_professional",
                "formality_level": "high",
                "name_format": "first_last",
                "phone_format": "+33-X-XX-XX-XX-XX",
                "date_format": "DD/MM/YYYY",
                "time_format": "24_hour",
                "currency": "EUR",
                "professional_titles": ["M.", "Mme.", "Dr.", "Prof."],
                "communication_style": "formal_structured",
                "interview_expectations": "formal, well_prepared, intellectual_discussion"
            },
            "de": {
                "greeting_style": "formal_professional",
                "formality_level": "high",
                "name_format": "first_last",
                "phone_format": "+49-XXX-XXXXXXX",
                "date_format": "DD.MM.YYYY",
                "time_format": "24_hour",
                "currency": "EUR",
                "professional_titles": ["Herr", "Frau", "Dr.", "Prof."],
                "communication_style": "direct_structured",
                "interview_expectations": "punctual, thorough, technical_competence"
            },
            "it": {
                "greeting_style": "warm_professional",
                "formality_level": "medium_high",
                "name_format": "first_last",
                "phone_format": "+39-XXX-XXX-XXXX",
                "date_format": "DD/MM/YYYY",
                "time_format": "24_hour",
                "currency": "EUR",
                "professional_titles": ["Sig.", "Sig.ra", "Dott.", "Prof."],
                "communication_style": "expressive_professional",
                "interview_expectations": "personable, passionate, competent"
            },
            "pt": {
                "greeting_style": "warm_professional",
                "formality_level": "medium_high",
                "name_format": "first_last",
                "phone_format": "+55-XX-XXXXX-XXXX",
                "date_format": "DD/MM/YYYY",
                "time_format": "24_hour",
                "currency": "BRL/EUR",
                "professional_titles": ["Sr.", "Sra.", "Dr.", "Prof."],
                "communication_style": "relationship_focused",
                "interview_expectations": "friendly, competent, team_oriented"
            },
            "ru": {
                "greeting_style": "formal_professional",
                "formality_level": "high",
                "name_format": "first_patronymic_last",
                "phone_format": "+7-XXX-XXX-XX-XX",
                "date_format": "DD.MM.YYYY",
                "time_format": "24_hour",
                "currency": "RUB",
                "professional_titles": ["Господин", "Госпожа", "Доктор"],
                "communication_style": "formal_hierarchical",
                "interview_expectations": "respectful, well_prepared, technical_depth"
            },
            "zh": {
                "greeting_style": "respectful_professional",
                "formality_level": "high",
                "name_format": "family_first",
                "phone_format": "+86-XXX-XXXX-XXXX",
                "date_format": "YYYY/MM/DD",
                "time_format": "24_hour",
                "currency": "CNY",
                "professional_titles": ["先生", "女士", "博士", "教授"],
                "communication_style": "hierarchical_respectful",
                "interview_expectations": "humble, prepared, respect_for_authority"
            },
            "ja": {
                "greeting_style": "very_formal_professional",
                "formality_level": "very_high",
                "name_format": "family_first",
                "phone_format": "+81-XX-XXXX-XXXX",
                "date_format": "YYYY/MM/DD",
                "time_format": "24_hour",
                "currency": "JPY",
                "professional_titles": ["さん", "様", "博士", "教授"],
                "communication_style": "extremely_polite",
                "interview_expectations": "extremely_polite, humble, group_harmony"
            },
            "ko": {
                "greeting_style": "respectful_professional",
                "formality_level": "high",
                "name_format": "family_first",
                "phone_format": "+82-XX-XXXX-XXXX",
                "date_format": "YYYY.MM.DD",
                "time_format": "24_hour",
                "currency": "KRW",
                "professional_titles": ["씨", "님", "박사", "교수"],
                "communication_style": "hierarchical_respectful",
                "interview_expectations": "respectful, age_hierarchy_aware, team_oriented"
            },
            "hi": {
                "greeting_style": "respectful_warm",
                "formality_level": "medium_high",
                "name_format": "first_last",
                "phone_format": "+91-XXXXX-XXXXX",
                "date_format": "DD/MM/YYYY",
                "time_format": "12_hour",
                "currency": "INR",
                "professional_titles": ["श्री", "श्रीमती", "डॉ.", "प्रो."],
                "communication_style": "respectful_relationship_focused",
                "interview_expectations": "respectful, family_context_ok, educational_background"
            },
            "ar": {
                "greeting_style": "formal_respectful",
                "formality_level": "high",
                "name_format": "first_father_family",
                "phone_format": "+XXX-X-XXX-XXXX",
                "date_format": "DD/MM/YYYY",
                "time_format": "12_hour",
                "currency": "local",
                "professional_titles": ["السيد", "السيدة", "الدكتور", "الأستاذ"],
                "communication_style": "formal_respectful",
                "interview_expectations": "respectful, religious_considerations, family_context"
            }
        }
        
        # Default context for languages not specifically defined
        default_context = {
            "greeting_style": "professional",
            "formality_level": "medium",
            "name_format": "first_last",
            "phone_format": "international",
            "date_format": "DD/MM/YYYY",
            "time_format": "24_hour",
            "currency": "local",
            "professional_titles": ["Mr.", "Ms.", "Dr."],
            "communication_style": "professional",
            "interview_expectations": "professional, competent, prepared"
        }
        
        return cultural_contexts.get(language, default_context)
    
    def adapt_greeting_for_culture(self, language: str, base_greeting: str) -> str:
        """
        Adapt a greeting based on cultural context.
        
        Args:
            language: Target language code
            base_greeting: Base greeting message
            
        Returns:
            Culturally adapted greeting
        """
        context = self.get_cultural_context(language)
        
        # Add cultural adaptations based on greeting style
        if context["greeting_style"] == "very_formal_professional":
            return f"🙏 {base_greeting}\n\nI will conduct this interview with the utmost respect and professionalism."
        elif context["greeting_style"] == "formal_professional":
            return f"🤝 {base_greeting}\n\nI look forward to learning about your professional background."
        elif context["greeting_style"] == "warm_professional":
            return f"😊 {base_greeting}\n\nI'm excited to learn about you and your experience!"
        elif context["greeting_style"] == "respectful_warm":
            return f"🙏 {base_greeting}\n\nI hope you and your family are doing well. Let's begin our conversation."
        elif context["greeting_style"] == "respectful_professional":
            return f"🙏 {base_greeting}\n\nThank you for taking the time to speak with me today."
        else:  # casual_professional or default
            return f"👋 {base_greeting}\n\nLet's get started with your interview!"
    
    def validate_cultural_data_format(self, data_type: str, value: str, language: str) -> Tuple[bool, str]:
        """
        Validate data format based on cultural context.
        
        Args:
            data_type: Type of data (name, phone, etc.)
            value: Value to validate
            language: Language/culture context
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        context = self.get_cultural_context(language)
        
        if data_type == "name":
            return self._validate_name_format(value, context)
        elif data_type == "phone":
            return self._validate_phone_format(value, context)
        elif data_type == "date":
            return self._validate_date_format(value, context)
        else:
            return True, ""
    
    def _validate_name_format(self, name: str, context: Dict) -> Tuple[bool, str]:
        """Validate name format based on cultural context."""
        if not name or not name.strip():
            return False, "Name cannot be empty"
        
        name_parts = name.strip().split()
        
        if context["name_format"] == "first_last":
            if len(name_parts) < 2:
                return False, "Please provide both first and last name"
        elif context["name_format"] == "first_paternal_maternal":
            if len(name_parts) < 2:
                return False, "Please provide at least first name and paternal surname"
        elif context["name_format"] == "family_first":
            if len(name_parts) < 2:
                return False, "Please provide both family and given name"
        elif context["name_format"] == "first_patronymic_last":
            if len(name_parts) < 2:
                return False, "Please provide at least first and last name"
        
        return True, ""
    
    def _validate_phone_format(self, phone: str, context: Dict) -> Tuple[bool, str]:
        """Validate phone format based on cultural context."""
        if not phone or not phone.strip():
            return False, "Phone number cannot be empty"
        
        # Basic validation - contains digits and common phone characters
        phone_clean = re.sub(r'[^\d+\-\s\(\)]', '', phone)
        if len(phone_clean) < 7:
            return False, f"Phone number seems too short. Expected format: {context['phone_format']}"
        
        return True, ""
    
    def _validate_date_format(self, date: str, context: Dict) -> Tuple[bool, str]:
        """Validate date format based on cultural context."""
        if not date or not date.strip():
            return False, "Date cannot be empty"
        
        # Basic date validation
        date_patterns = {
            "DD/MM/YYYY": r'\d{1,2}/\d{1,2}/\d{4}',
            "MM/DD/YYYY": r'\d{1,2}/\d{1,2}/\d{4}',
            "YYYY/MM/DD": r'\d{4}/\d{1,2}/\d{1,2}',
            "DD.MM.YYYY": r'\d{1,2}\.\d{1,2}\.\d{4}',
            "YYYY.MM.DD": r'\d{4}\.\d{1,2}\.\d{1,2}'
        }
        
        expected_format = context["date_format"]
        pattern = date_patterns.get(expected_format, r'\d{1,2}[/\-.]\d{1,2}[/\-.]\d{4}')
        
        if not re.match(pattern, date.strip()):
            return False, f"Date format should be {expected_format}"
        
        return True, "" 