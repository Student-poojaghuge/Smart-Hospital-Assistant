
TRANSLATIONS = {

    "English": {
        "dashboard": "Dashboard",
        "welcome": "Welcome to Smart Hospital Assistant",
        "book_appointment": "Book Appointment",
        "my_appointments": "My Appointments",
        "medical_records": "Medical Records",
        "medicines": "Medicines",
        "emergency": "Emergency Assessment",
        "ai_assistant": "AI Health Assistant",
        "profile": "Profile",
        "logout": "Logout",
        "select_language": "Select Language",
        "continue": "Continue"
    },

    "Marathi": {
        "dashboard": "डॅशबोर्ड",
        "welcome": "स्मार्ट हॉस्पिटल असिस्टंटमध्ये आपले स्वागत आहे",
        "book_appointment": "अपॉइंटमेंट बुक करा",
        "my_appointments": "माझ्या अपॉइंटमेंट्स",
        "medical_records": "मेडिकल रेकॉर्ड्स",
        "medicines": "औषधे",
        "emergency": "आपत्कालीन तपासणी",
        "ai_assistant": "AI आरोग्य सहाय्यक",
        "profile": "प्रोफाइल",
        "logout": "लॉगआउट",
        "select_language": "भाषा निवडा",
        "continue": "पुढे जा"
    },

    "Hindi": {
        "dashboard": "डैशबोर्ड",
        "welcome": "स्मार्ट हॉस्पिटल असिस्टेंट में आपका स्वागत है",
        "book_appointment": "अपॉइंटमेंट बुक करें",
        "my_appointments": "मेरी अपॉइंटमेंट्स",
        "medical_records": "मेडिकल रिकॉर्ड्स",
        "medicines": "दवाइयाँ",
        "emergency": "आपातकालीन जांच",
        "ai_assistant": "AI स्वास्थ्य सहायक",
        "profile": "प्रोफ़ाइल",
        "logout": "लॉगआउट",
        "select_language": "भाषा चुनें",
        "continue": "जारी रखें"
    }
}


def get_text(language, key):
    return TRANSLATIONS.get(
        language,
        TRANSLATIONS["English"]
    ).get(
        key,
        key
    )
