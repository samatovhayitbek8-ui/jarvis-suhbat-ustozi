JARVIS - ERKIN AI SUHBAT (mobil va kompyuter)

Yangi imkoniyatlar:
- Erkin suhbat: istalgan mavzuda Gemini AI bilan gaplashish.
- Ovozli rejim: bir marta ishga tushirilgach, JARVIS tinglaydi, javobni AI ga yuboradi, javobni ovoz chiqarib o'qiydi va yana tinglaydi.
- Matn bilan ham yuborish mumkin. Enter - yuborish, Shift+Enter - yangi qator.
- Oldingi suhbatning so'nggi xabarlari kontekst sifatida saqlanadi (sahifa ochiq turgan vaqt davomida).
- Avvalgi 240 ta suhbat savoli va imtihon rejimi saqlanadi.

Render sozlamalari:
- GEMINI_API_KEY environment variable bo'lishi kerak.
- GEMINI_MODEL ixtiyoriy; standart model gemini-3.8-flash.
- Kalitni HTML yoki GitHub fayliga yozmang.

Ishga tushirish:
1. ZIP ichidagi Update_JARVIS_Erkin_Suhbat.ps1 faylini .ps1 sifatida ishga tushiring.
2. Skript mavjud Desktop\JARVIS_Mobile_Web_GitHub loyihasining zaxira nusxasini yaratadi, yangilangan fayllarni joylaydi va GitHub main branch'iga yuboradi.
3. Render yangi commitni deploy qilgach, https://jarvis-suhbat-ustozi.onrender.com saytini qayta oching.
4. Sahifadagi "JARVIS bilan erkin suhbat" qismida "Jonli suhbatni boshlash" ni bosing va Chrome mikrofon ruxsatini bering.

Eslatma:
- Ovozli nutqni tanish Chrome/Android brauzerining imkoniyatlariga va tarmoq mavjudligiga bog'liq.
- Ovoz javoblari serverdagi edge-tts orqali tayyorlanadi; xizmat ishlamasa, brauzer ovoziga o'tishi mumkin.
- Gemini API bepul tarifida limit bo'lishi mumkin.
