import os
import subprocess
import torch
import customtkinter as ctk
from tkinter import messagebox, filedialog
from moviepy import VideoFileClip, AudioFileClip

# --- وظيفة معالجة الفيديو وعزل الصوت ---
def clean_process():
    # جلب المسارات والقيم من واجهة المستخدم
    input_path = entry1.get()
    output_path = entry2.get()
    output_format = combo.get()

    # التحقق من أن المستخدم اختار الملفات المطلوبة
    if not input_path or not output_path:
        messagebox.showerror("خطأ", "الرجاء اختيار ملف المدخلات ومكان الحفظ!")
        return

    try:
        # تحديد المعالج المستخدم: CUDA لكرت الشاشة (سريع) أو CPU للمعالج العادي
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # تفريغ ذاكرة كرت الشاشة المؤقتة لضمان استقرار النظام
        if device == "cuda": torch.cuda.empty_cache()

        # بناء أمر التشغيل لأداة Demucs لعزل صوت الغناء فقط (vocals)
        # استخدمنا --shifts 1 لتقليل الضغط على الذاكرة وزيادة السرعة
        command = f'python -m demucs -d {device} --two-stems=vocals --shifts 1 "{input_path}"'
        
        messagebox.showinfo("بدء المعالجة", f"بدأت المعالجة باستخدام وحدة: {device.upper()}...")
        
        # تنفيذ الأمر الخارجي وانتظار انتهائه
        subprocess.run(command, shell=True, check=True)

        # استخراج اسم الفيديو بدون الصيغة لتحديد موقع الملف المستخرج
        video_name = os.path.splitext(os.path.basename(input_path))[0]
        vocals_wav = os.path.join("separated", "htdemucs", video_name, "vocals.wav")
        
        # تحديد المسار النهائي للملف الناتج
        final_output = f"{output_path}.{output_format}"

        # إذا اختار المستخدم صيغة MP4، يتم دمج الصوت المعزول مع الفيديو الأصلي
        if output_format == "mp4":
            video_clip = VideoFileClip(input_path)
            clean_audio = AudioFileClip(vocals_wav)
            # استبدال صوت الفيديو الأصلي بالصوت النقي
            final_video = video_clip.with_audio(clean_audio)
            # تصدير ملف الفيديو الجديد مع تحديد معالجات الفيديو والصوت
            final_video.write_videofile(final_output, codec="libx264", audio_codec="aac", threads=4)
            # إغلاق الملفات لتحرير الذاكرة
            video_clip.close()
            clean_audio.close()
        else:
            # إذا اختار المستخدم WAV، يتم نسخ ملف الصوت المستخرج فقط
            import shutil
            shutil.copy(vocals_wav, final_output)

        messagebox.showinfo("نجاح", "تمت عملية التنقية والحفظ بنجاح!")

    except Exception as e:
        messagebox.showerror("خطأ تقني", f"حدث خطأ أثناء المعالجة: {e}")

# --- وظائف واجهة المستخدم الرسومية ---

def browse_file():
    # فتح نافذة لاختيار ملف الفيديو من الجهاز
    file_path = filedialog.askopenfilename(title="اختر ملف الفيديو")
    if file_path:
        entry1.delete(0, ctk.END)
        entry1.insert(0, file_path)

def browse_file_save():
    # فتح نافذة لتحديد مكان واسم حفظ الملف الناتج
    file_path = filedialog.asksaveasfilename(title="حدد مكان الحفظ")
    if file_path:
        entry2.delete(0, ctk.END)
        entry2.insert(0, file_path)

# إعداد المظهر العام للواجهة (الوضع الداكن)
ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.geometry("400x500")
app.title("RaziVocals - الذكاء الاصطناعي لنقاء الصوت")

# إنشاء العناصر الرسومية (العناوين، الحقول، الأزرار)
label = ctk.CTkLabel(app, text="مرحباً بك في تطبيق رازي!", font=ctk.CTkFont(size=22, weight="bold"))
label.pack(pady=20)

entry1 = ctk.CTkEntry(app, placeholder_text="مسار ملف الفيديو الأصلي", width=300)
entry1.pack(pady=10, padx=20)

btn_browse = ctk.CTkButton(app, text="اختيار الفيديو", command=browse_file)
btn_browse.pack(pady=5)

label_fmt = ctk.CTkLabel(app, text="اختر صيغة الإخراج:")
label_fmt.pack(pady=5)

combo = ctk.CTkComboBox(app, values=["mp4", "wav"]) 
combo.pack(pady=5)

entry2 = ctk.CTkEntry(app, placeholder_text="اسم ومسار ملف الحفظ", width=300)
entry2.pack(pady=10, padx=20)

btn_browse_save = ctk.CTkButton(app, text="تحديد مكان الحفظ", command=browse_file_save)
btn_browse_save.pack(pady=5)

# زر البدء الأساسي
btn_clean = ctk.CTkButton(app, text="بدء تنقية الفيديو", fg_color="#27ae60", hover_color="#2ecc71", command=clean_process)
btn_clean.pack(pady=30)

label_dev = ctk.CTkLabel(app, text="تطوير: رازي سلطان", font=ctk.CTkFont(size=12))
label_dev.pack(side="bottom", pady=10)

# تشغيل الحلقة الرئيسية للتطبيق
app.mainloop()
