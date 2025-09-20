import os
import threading
from tkinter import *
from tkinter import ttk, messagebox, simpledialog
import yt_dlp
import time

stop_flag = False  
speed_threshold = 5000  

def normalize_url(url):
    if "youtu.be" in url:
        video_id = url.split("/")[-1].split("?")[0]
        return f"https://www.youtube.com/watch?v={video_id}"
    return url

def add_url(event=None):
    url = url_entry.get().strip()
    if url:
        url = normalize_url(url)
        url_listbox.insert(END, url)
        url_entry.delete(0, END)

def remove_selected():
    selected = url_listbox.curselection()
    for index in reversed(selected):
        url_listbox.delete(index)

def clear_list():
    url_listbox.delete(0, END)

settings = {
    'concurrent_fragment_downloads': 5,
    'fragment_retries': 10,
    'retry_sleep': 5,
    'format': 'MP4',
    'theme': 'beyaz'
}

def open_settings():
    popup = Toplevel(root)
    popup.title("Ayarlar")
    popup.geometry("300x250")

    Label(popup, text="Concurrent Fragment Downloads:").pack()
    cfd_entry = Entry(popup)
    cfd_entry.pack()
    cfd_entry.insert(0, str(settings['concurrent_fragment_downloads']))

    Label(popup, text="Fragment Retries:").pack()
    fr_entry = Entry(popup)
    fr_entry.pack()
    fr_entry.insert(0, str(settings['fragment_retries']))

    Label(popup, text="Retry Sleep (saniye):").pack()
    rs_entry = Entry(popup)
    rs_entry.pack()
    rs_entry.insert(0, str(settings['retry_sleep']))

    def save_settings():
        try:
            settings['concurrent_fragment_downloads'] = int(cfd_entry.get())
            settings['fragment_retries'] = int(fr_entry.get())
            settings['retry_sleep'] = int(rs_entry.get())
            settings['theme'] = theme_var.get()
            settings['format'] = format_var.get()
            apply_theme()
            popup.destroy()
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayılar girin!")

    Button(popup, text="Kaydet", command=save_settings).pack(pady=10)

def progress_hook(d):
    global stop_flag
    if stop_flag:
        raise Exception("İndirme durduruldu.")
    if d['status'] == 'downloading':
        speed = d.get('speed', 0)
        if speed and speed < speed_threshold:
            raise Exception("Hız çok düşük, yeniden başlatılıyor...")

def download_with_yt_dlp(url):
    os.makedirs("indirilenler", exist_ok=True)
    start_time = start_entry.get().strip()
    end_time = end_entry.get().strip()

    ydl_opts = {
        'outtmpl': 'indirilenler/%(title)s.%(ext)s',
        'noplaylist': False,
        'quiet': True,
        'no_warnings': True,
        'concurrent_fragment_downloads': settings['concurrent_fragment_downloads'],
        'fragment_retries': settings['fragment_retries'],
        'retry_sleep': settings['retry_sleep'],
        'progress_hooks': [progress_hook]
    }

    if settings['format'] == "MP3":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        ydl_opts.update({'format': 'best[ext=mp4]/best'})

    if start_time or end_time:
        section = f"*{start_time if start_time else '0'}-{end_time if end_time else ''}"
        ydl_opts['download_sections'] = [section]

    while True:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            break 
        except Exception as e:
            if "Hız çok düşük" in str(e):
                time.sleep(1)  
                continue
            elif "İndirme durduruldu" in str(e):
                break
            else:
                raise e

def download_all_thread():
    global stop_flag
    stop_flag = False
    urls = url_listbox.get(0, END)
    if not urls:
        messagebox.showwarning("Uyarı", "Video ekle!")
        return

    progress_bar['maximum'] = len(urls)
    count = 0

    for url in urls:
        if stop_flag:
            break
        try:
            download_with_yt_dlp(url)
            count += 1
            update_progress(count)
        except Exception as e:
            messagebox.showerror("Hata", f"{url} inmedi:\n{str(e)}")

    messagebox.showinfo("Tamamlandı", f"{count} video başarıyla indirildi.")

def update_progress(value):
    progress_bar['value'] = value
    progress_label.config(text=f"{value}/{progress_bar['maximum']} tamamlandı")
    root.update_idletasks()

def start_download_thread():
    thread = threading.Thread(target=download_all_thread)
    thread.start()

def stop_download():
    global stop_flag
    stop_flag = True

def apply_theme():
    theme = settings['theme']
    bg = "#2e2e2e" if theme == "siyah" else "SystemButtonFace"
    fg = "white" if theme == "siyah" else "black"
    root.configure(bg=bg)
    for widget in root.winfo_children():
        try:
            widget.configure(bg=bg, fg=fg)
        except:
            pass

root = Tk()
root.title("Yutup")
root.geometry("600x700")

Label(root, text="URL:").pack(pady=5)
url_entry = Entry(root, width=70)
url_entry.pack()
url_entry.bind("<Return>", add_url)

btn_frame = Frame(root)
btn_frame.pack(pady=5)

Button(btn_frame, text="Ekle", command=add_url).pack(side=LEFT, padx=5)
Button(btn_frame, text="Sil", command=remove_selected).pack(side=LEFT, padx=5)
Button(btn_frame, text="Temizle", command=clear_list).pack(side=LEFT, padx=5)
Button(btn_frame, text="Ayarlar", command=open_settings).pack(side=LEFT, padx=5)
Button(btn_frame, text="Durdur", command=stop_download).pack(side=LEFT, padx=5)

# Format ve Tema
format_var = StringVar(value=settings['format'])
Radiobutton(root, text="MP4 (Video)", variable=format_var, value="MP4").pack()
Radiobutton(root, text="MP3 (Ses)", variable=format_var, value="MP3").pack()

theme_var = StringVar(value=settings['theme'])
Label(root, text="Tema:").pack()
ttk.Combobox(root, textvariable=theme_var, values=["beyaz", "siyah"]).pack()

# Süre aralığı
Label(root, text="Başlangıç (HH:MM:SS):").pack()
start_entry = Entry(root, width=20)
start_entry.pack()
Label(root, text="Bitiş (HH:MM:SS):").pack()
end_entry = Entry(root, width=20)
end_entry.pack()

Button(root, text="İndir", command=start_download_thread).pack(pady=10)

Label(root, text="Liste").pack()
url_listbox = Listbox(root, width=70, height=6)
url_listbox.pack()

progress_bar = ttk.Progressbar(root, length=500)
progress_bar.pack(pady=5)
progress_label = Label(root, text="0/0 tamamlandı")
progress_label.pack()

root.mainloop()
