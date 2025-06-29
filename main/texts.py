import os
import sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # Add parent directory
sys.path.append((os.path.dirname(__file__)))  # Add current directory

from functions.get_platform import platform

PROGRAM_NAME = "AutoSubSync"
GITHUB_URL = "https://github.com/denizsafak/AutoSubSync"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/denizsafak/AutoSubSync/refs/heads/main/main/VERSION"
GITHUB_LATEST_RELEASE_URL = "https://github.com/denizsafak/AutoSubSync/releases/latest"
ARABIC_LANGUAGES = {
    "ar",  # Arabic
    "fa",  # Farsi (Persian)
    "ur",  # Urdu
    "ps",  # Pashto
    "sd",  # Sindhi
    "ug",  # Uyghur
}

if platform != "Darwin":
    from bidi.algorithm import get_display
    import arabic_reshaper


class TranslationDict(dict):
    def __missing__(self, key):
        return self.get("en", "")

    if platform != "Darwin":
        # Fix arabic text display
        def __getitem__(self, key):
            text = super().__getitem__(key)
            if key in ARABIC_LANGUAGES:
                reshaped_text = arabic_reshaper.reshape(text)
                return get_display(reshaped_text)
            return text


TOOLTIP_SAVE_TO_DESKTOP = {
    "en": "Check this box if you want to save the subtitle to your Desktop. If unchecked it will be saved next to the input subtitle.",
    "es": "Marque esta casilla si desea guardar el subtítulo en su escritorio. Si no está marcado, se guardará junto al subtítulo de entrada.",
    "tr": "Altyazıyı masaüstüne kaydetmek istiyorsanız bu kutuyu işaretleyin. İşaretlenmezse, girdi altyazının yanına kaydedilecektir.",
    "zh": "如果您想将字幕保存到桌面，请选中此框。如果未选中，它将保存在输入字幕旁边。",
    "ru": "Отметьте этот флажок, если хотите сохранить субтитры на рабочем столе. Если флажок не установлен, он будет сохранен рядом с входными субтитрами.",
    "pl": "Zaznacz to pole, jeśli chcesz zapisać napisy na pulpicie. Jeśli nie zaznaczono, zostanie zapisany obok napisów wejściowych.",
    "uk": "Позначте цей прапорець, якщо хочете зберегти субтитри на робочому столі. Якщо не позначено, вони будуть збережені поруч із вхідними субтитрами.",
    "ja": "字幕をデスクトップに保存する場合は、このボックスをチェックしてください。チェックしない場合、入力字幕の横に保存されます。",
    "ko": "자막을 바탕 화면에 저장하려면 이 상자를 선택하세요. 선택하지 않으면 입력 자막 옆에 저장됩니다.",
    "hi": "अगर आप उपशीर्षक को डेस्कटॉप पर सहेजना चाहते हैं तो इस बॉक्स को चेक करें। अगर अनचेक है, तो यह इनपुट उपशीर्षक के पास सहेजा जाएगा।",
    "bn": "সাবটাইটেলটি আপনার ডেস্কটপে সংরক্ষণ করতে চাইলে এই বাক্সটি চেক করুন। যদি আনচেক করা থাকে, এটি ইনপুট সাবটাইটেলের পাশে সংরক্ষিত হবে।",
    "it": "Seleziona questa casella se desideri salvare il sottotitolo sul desktop. Se deselezionato, verrà salvato accanto al sottotitolo di input.",
    "fr": "Cochez cette case si vous souhaitez enregistrer le sous-titre sur votre bureau. Si décoché, il sera enregistré à côté du sous-titre d'entrée.",
    "de": "Markieren Sie dieses Kästchen, wenn Sie die Untertiteldatei auf Ihrem Desktop speichern möchten. Wenn nicht markiert, wird sie neben den Eingabe-Untertiteln gespeichert.",
    "pt": "Marque esta caixa se quiser salvar a legenda na sua área de trabalho. Se desmarcado, será salvo ao lado da legenda de entrada.",
    "ar": "حدد هذا المربع إذا كنت تريد حفظ العنوان الفرعي على سطح المكتب. إذا لم يتم تحديدها، فسيتم حفظها بجوار العنوان الفرعي المدخل.",
    "vi": "Đánh dấu vào ô này nếu bạn muốn lưu phụ đề vào Máy tính của bạn. Nếu không được chọn, nó sẽ được lưu bên cạnh phụ đề đầu vào.",
    "fa": "اگر می‌خواهید زیرنویس را در رومیزی خود ذخیره کنید، این جعبه را علامت بزنید. اگر علامت گذاری نشود، در کنار زیرنویس ورودی ذخیره می‌شود.",
    "id": "Centang kotak ini jika Anda ingin menyimpan subtitle ke Desktop Anda. Jika tidak dicentang, itu akan disimpan di samping subtitle masukan.",
    "ms": "Tandai kotak ini jika anda ingin menyimpan sari kata pada Desktop anda. Jika dinyahtandai, ia akan disimpan di sebelah sari kata input.",
    "th": "ทำเครื่องหมายในช่องนี้หากคุณต้องการบันทึกคำบรรยายลงในเดสก์ท็อป หากไม่ทำเครื่องหมาย คำบรรยายจะถูกบันทึกไว้ข้างคำบรรยายที่ป้อน",
    "ur": "اگر آپ سب ٹائٹل اپنے ڈیسک ٹاپ پر محفوظ کرنا چاہتے ہیں تو یہ باکس چیک کریں۔ اگر بغیر چیک کیے چھوڑ دیا جائے تو یہ ان پٹ سب ٹائٹل کے ساتھ محفوظ ہوگا。",
}

# Continue with the rest of the original content...