import os
import sounddevice as sd
import soundfile as sf
from elevenlabs.client import ElevenLabs
from io import BytesIO
import tempfile
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
from tkinter import ttk

# ElevenLabs API
client = ElevenLabs(
    api_key="YOUR_API_KEy",
)

def record_audio_to_bytes(duration=5, samplerate=44100):
    print(f"🎤 Recording for {duration} seconds... Speak now")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        filename = tmpfile.name
        sf.write(filename, recording, samplerate)

    with open(filename, "rb") as f:
        audio_data = BytesIO(f.read())

    os.remove(filename)

    return audio_data

def save_text():
    text = transcription_text.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("تحذير", "لا يوجد نص للحفظ!")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text Files", "*.txt")])
    if file_path:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("نجاح", "تم حفظ الملف بنجاح!")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل الحفظ: {e}")

def upload_audio_file():
    file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if not file_path:
        return

    language_code = lang_var.get()
    if language_code == "":
        messagebox.showwarning("تحذير", "من فضلك اختر اللغة أولاً")
        return

    try:
        progress_bar.start()
        root.update()

        with open(file_path, "rb") as f:
            audio_data = BytesIO(f.read())

        transcription = client.speech_to_text.convert(
            file=audio_data,
            model_id="scribe_v1",
            tag_audio_events=True,
            language_code=language_code,
            diarize=True
        )

        transcription_text.delete("1.0", tk.END)
        transcription_text.insert(tk.END, transcription.text)

    except Exception as e:
        print("❌ Error during speech-to-text:", e)
        messagebox.showerror("خطأ", f"حدث خطأ أثناء تحويل الصوت إلى نص: {e}")

    finally:
        progress_bar.stop()
        root.update()

def run_speech_to_text():
    language_code = lang_var.get()
    if language_code == "":
        messagebox.showwarning("تحذير", "من فضلك اختر اللغة أولاً")
        return

    try:
        duration = int(duration_var.get())
        audio_data = record_audio_to_bytes(duration=duration)
        print("⏳ Sending audio to ElevenLabs...")

        progress_bar.start()
        root.update()

        transcription = client.speech_to_text.convert(
            file=audio_data,
            model_id="scribe_v1",
            tag_audio_events=True,
            language_code=language_code,
            diarize=True
        )

        transcription_text.delete("1.0", tk.END)
        transcription_text.insert(tk.END, transcription.text)

    except ValueError:
        messagebox.showerror("خطأ", "مدة التسجيل يجب أن تكون عدد صحيح")
    except Exception as e:
        print("❌ Error during speech-to-text:", e)
        messagebox.showerror("خطأ", f"حدث خطأ أثناء تحويل الصوت إلى نص: {e}")

    finally:
        progress_bar.stop()
        root.update()

def start_transcription_thread():
    transcription_thread = threading.Thread(target=run_speech_to_text)
    transcription_thread.start()

# --- واجهة المستخدم ---

root = tk.Tk()
root.title("Speech-to-Text Application")
root.geometry("800x600")  # حجم النافذة الابتدائي
root.resizable(True, True)  # السماح بتكبير وتصغير النافذة

title_label = tk.Label(root, text="Speech-to-Text Converter", font=("Arial", 18, "bold"))
title_label.pack(pady=15)

lang_label = tk.Label(root, text="Choose Language:")
lang_label.pack()

languages = {
    "English": "en",
    "Arabic": "ar",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Chinese": "zh",
    "Japanese": "ja",
}

lang_var = tk.StringVar()
lang_dropdown = ttk.Combobox(root, textvariable=lang_var, values=list(languages.values()), state="readonly")
lang_dropdown.pack(pady=5)
lang_dropdown.set("en")

duration_label = tk.Label(root, text="Recording Duration (seconds):")
duration_label.pack()
duration_var = tk.StringVar(value="5")
duration_entry = tk.Entry(root, textvariable=duration_var, width=5, justify='center')
duration_entry.pack(pady=5)

start_button = tk.Button(root, text="🎙️ Record & Transcribe", command=start_transcription_thread,
                         width=25, height=2, bg="#4CAF50", fg="white", font=("Arial", 12))
start_button.pack(pady=10)

upload_button = tk.Button(root, text="📁 Upload Audio File", command=upload_audio_file,
                          width=25, height=2, bg="#2196F3", fg="white", font=("Arial", 12))
upload_button.pack(pady=10)

transcription_text = tk.Text(root, height=8, font=("Arial", 12), wrap="word")
transcription_text.pack(padx=15, pady=10, fill="both", expand=True)  # يسمح بالتمدد

save_button = tk.Button(root, text="💾 Save Text to File", command=save_text,
                        width=25, height=2, bg="#FF9800", fg="white", font=("Arial", 12))
save_button.pack(pady=10)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="indeterminate")
progress_bar.pack(pady=10, fill="x", expand=True) 

root.mainloop()
