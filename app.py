import os
import subprocess
import torch
import customtkinter as ctk
from tkinter import messagebox, filedialog
from moviepy import VideoFileClip, AudioFileClip

# إعدادات الموديلات المحلية
current_dir = os.path.dirname(os.path.abspath(__file__))
os.environ["TORCH_HOME"] = os.path.join(current_dir, "models")

def clean_process():
    input_path = entry1.get()
    output_path = entry2.get()
    output_format = combo.get()

    if not input_path or not output_path:
        messagebox.showerror("Error", "الرجاء اختيار ملف المدخلات ومكان الحفظ!")
        return

    try:
        # 1. تحديد الجهاز (GPU أو CPU)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # 2. تنظيف الرام قبل البدء
        if device == "cuda": torch.cuda.empty_cache()

        # 3. بناء الأمر (بدون تحديد segment يدوي لتجنب الخطأ)
        # أضفنا --shifts 1 لزيادة السرعة وتقليل استهلاك الرام
        command = f'python -m demucs -d {device} --two-stems=vocals --shifts 1 "{input_path}"'
        
        messagebox.showinfo("بدء العمل", f"بدأت المعالجة باستخدام {device.upper()}...")
        subprocess.run(command, shell=True, check=True)

        # 4. معالجة النتيجة
        video_name = os.path.splitext(os.path.basename(input_path))[0]
        vocals_wav = os.path.join("separated", "htdemucs", video_name, "vocals.wav")
        
        # التأكد من المسار النهائي
        final_output = f"{output_path}.{output_format}"

        if output_format == "mp4":
            video_clip = VideoFileClip(input_path)
            clean_audio = AudioFileClip(vocals_wav)
            final_video = video_clip.with_audio(clean_audio)
            final_video.write_videofile(final_output, codec="libx264", audio_codec="aac", threads=4)
            video_clip.close()
            clean_audio.close()
        else:
            import shutil
            shutil.copy(vocals_wav, final_output)

        messagebox.showinfo("نجاح", f"تم الحفظ بنجاح!")

    except Exception as e:
        messagebox.showerror("Error", f"حدث خطأ: {e}")

# --- واجهة المستخدم (نفس كودك السابق مع ربط الزر) ---
def browse_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        entry1.delete(0, ctk.END)
        entry1.insert(0, file_path)

def browse_file_save():
    file_path = filedialog.asksaveasfilename()
    if file_path:
        entry2.delete(0, ctk.END)
        entry2.insert(0, file_path)

ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.geometry("300x400")
app.title("Vocale - AI Power")

label = ctk.CTkLabel(app, text="Welcome to Vocale!", font=ctk.CTkFont(size=20, weight="bold"))
label.pack(pady=20)

entry1 = ctk.CTkEntry(app, placeholder_text="video path")
entry1.pack(pady=10, padx=20, fill="x")

btn_browse = ctk.CTkButton(app, text="Browse Video", command=browse_file)
btn_browse.pack(pady=10)

label1 = ctk.CTkLabel(app, text="Output Format:")
label1.pack(pady=5)

combo = ctk.CTkComboBox(app, values=["mp4", "wav"]) 
combo.pack(pady=5)

entry2 = ctk.CTkEntry(app, placeholder_text="output path and name")
entry2.pack(pady=10, padx=20, fill="x")

btn_browse_save = ctk.CTkButton(app, text="Browse Output", command=browse_file_save)
btn_browse_save.pack(pady=10)

btn_clean = ctk.CTkButton(app, text="Clean Video", fg_color="green", command=clean_process)
btn_clean.pack(pady=20)

labeldev = ctk.CTkLabel(app, text="Developed by Razi Sultan")
labeldev.pack(side="bottom")

app.mainloop()