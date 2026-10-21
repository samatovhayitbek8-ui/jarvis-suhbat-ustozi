JARVIS — TELEFON UCHUN WEB-ILOVA (PWA)
=======================================

Bu paket Android Chrome va boshqa zamonaviy telefon brauzerlariga mos responsive web-ilova.
Ichida PDFdan olingan 240 ta savol-javob, animatsiyali avatar, ovozli/matnli mashq va Microsoft onlayn o‘zbekcha TTS ko‘prigi bor.

MUHIM: Telefon mikrofonidan foydalanish uchun sayt HTTPS manzilida ochilishi shart. ZIP ichidagi HTML faylni telefonda oddiy file:// orqali ochish mikrofonni to‘liq ishlatmaydi. Shuning uchun ilovani internetdagi HTTPS hostingga joylash kerak.

HOSTINGGA JOYLASH (Render Blueprint orqali)
-------------------------------------------
1. ZIPni kompyuterga chiqar.
2. GitHub’da yangi repository yarat (masalan, jarvis-suhbat-ustozi). Ichidagi barcha fayl va public papkasini repository ildiziga joyla. ZIPning o‘zinigina yuklash yetarli emas — fayllarni chiqarib yukla.
3. render.com saytiga kirib GitHub bilan ulan.
4. Dashboard → New → Blueprint tanla va yangi repositoryni ko‘rsat.
5. Render render.yaml faylini ko‘rib, Python web xizmati yaratadi. JARVIS_ACCESS_TOKEN uchun tasodifiy maxfiy qiymat avtomatik yaratiladi.
6. Deploy tugagach, Render bergan https://...onrender.com manzilini telefonda Chrome orqali och.
7. Mikrofon so‘ralganda Allow/Ruxsat ber tugmasini bos. Chrome menyusi (⋮) → “Add to Home screen” yoki “Install app” orqali bosh ekranga qo‘shish mumkin.

ISHLASH SHARTLARI
-----------------
- Tabiiy Microsoft o‘zbekcha ovozi uchun internet zarur.
- Ovoz berish uchun Sardor yoki Madina tanlanadi.
- Ovozli javobni tanish Web Speech API orqali ishlaydi; eng maqbul qurilma Android + Chrome. iPhone/Safari nutqni tanish bo‘yicha cheklovlarga ega bo‘lishi mumkin.
- O‘rnatilgan PWA tashqi ovoz serveriga ulanadi. Servisga faqat suhbat matni (savollar / ovozda aytiladigan qisqa iboralar) yuboriladi.
- Render free xizmatida uyg‘onish/cold-start kechikishi bo‘lishi mumkin; bepul xizmatlarning mavjudligi va shartlari hosting provayderiga bog‘liq.

MAHALLIY SINOV (kompyuter)
--------------------------
Python 3.10+ kerak. Terminalda shu papkaga kirib:
    pip install -r requirements.txt
    python app.py
Lekin telefon mikrofoni uchun HTTPS hosting zarurligini unutmang; localhostdan boshqa HTTP IP manzillar ko‘pincha secure context hisoblanmaydi.

XAVFSIZLIK VA CHEKLOVLAR
------------------------
- Render Blueprint JARVIS_ACCESS_TOKEN ni tasodifiy generatsiya qiladi. Server TTS so‘rovlarini shu token bilan tekshiradi va IP bo‘yicha tezlik chegarasiga ega.
- Bu o‘quv uchun mo‘ljallangan shaxsiy vosita. Ovoz xizmatining uchinchi tomon shartlari va ishlashi o‘zgarishi mumkin.
- PDF matnidagi namuna javoblar savollarni avtomatik tekshirish uchun ishlatiladi. Algoritmik baho mazmuniy insoniy baholashning aynan o‘zi emas.


YANGI: IXTIYORIY AI BAHOLASH
-----------------------------
Sayt AI bo‘lmasa ham ishlaydi va mahalliy kalit-so‘z algoritmi bilan baholaydi. Mazmunni so‘zma-so‘z talab qilmaydigan AI baholashini yoqish uchun: Render Dashboard → jarvis-suhbat-ustozi → Environment → Add Environment Variable.
Key: OPENAI_API_KEY
Value: OpenAI API hisobingizdan olgan maxfiy API kalitingiz. Uni GitHub kodiga, HTML faylga yoki chatga yozmang. Keyin Save Changes/Deploy qiling. Ixtiyoriy model sozlamasi: OPENAI_MODEL=gpt-4.1-mini.
OpenAI API alohida hisob-kitob qilinadi; ChatGPT obunasi API krediti degani emas. AI yoqilganda savol, namunaviy javob va foydalanuvchi javobi baholash uchun OpenAI API’ga yuboriladi.

JONLI REJIM TUZATISHLARI
------------------------
Jonli suhbatda transkriptni qayta-qayta yozib yuborish muammosi uchun final/interim nutq natijalari alohida saqlanadi va bir xil takrorlangan iboralar tozalanadi. Jonli rejimda “Javobni tekshirish” tugmasi yashiriladi; 10 soniya sukutdan keyin avtomatik tekshiruv va keyingi savol ishlaydi.
