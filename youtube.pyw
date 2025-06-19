import os
import threading
from tkinter import *
from tkinter import ttk, messagebox
import yt_dlp

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

def download_with_yt_dlp(url, format_selected):
    os.makedirs("indirilenler", exist_ok=True)
    ydl_opts = {
        'outtmpl': 'indirilenler/%(title)s.%(ext)s',
        'noplaylist': False,  # Playlist desteklensin
        'quiet': True,
        'no_warnings': True,
    }

    if format_selected == "MP3":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:  # MP4
        ydl_opts.update({
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
        })

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def download_all_thread():
    urls = url_listbox.get(0, END)
    format_selected = format_var.get()
    progress_bar['maximum'] = len(urls)
    count = 0

    for url in urls:
        try:
            download_with_yt_dlp(url, format_selected)
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

def apply_theme():
    theme = theme_var.get()
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
root.geometry("600x480")

Label(root, text="URL:").pack(pady=5)
url_entry = Entry(root, width=70)
url_entry.pack()
url_entry.bind("<Return>", add_url)

btn_frame = Frame(root)
btn_frame.pack(pady=5)

Button(btn_frame, text="Ekle", command=add_url).pack(side=LEFT, padx=5)
Button(btn_frame, text="Sil", command=remove_selected).pack(side=LEFT, padx=5)
Button(btn_frame, text="Temizle", command=clear_list).pack(side=LEFT, padx=5)

format_var = StringVar(value="MP4")
Radiobutton(root, text="MP4 (Video)", variable=format_var, value="MP4").pack()
Radiobutton(root, text="MP3 (Ses)", variable=format_var, value="MP3").pack()

theme_var = StringVar(value="beyaz")
Label(root, text="Tema:").pack()
ttk.Combobox(root, textvariable=theme_var, values=["beyaz", "siyah"]).pack()
Button(root, text="Uygula", command=apply_theme).pack(pady=5)

Button(root, text="İndir", command=start_download_thread).pack(pady=10)

Label(root, text="Liste").pack()
url_listbox = Listbox(root, width=70, height=6)
url_listbox.pack()

progress_bar = ttk.Progressbar(root, length=500)
progress_bar.pack(pady=5)

progress_label = Label(root, text="0/0 tamamlandı")
progress_label.pack()

root.mainloop()
