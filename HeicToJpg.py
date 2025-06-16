import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from PIL import Image
import pillow_heif
from pathlib import Path
import threading

class HEICConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("HEIC → JPG Dönüştürücü")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # HEIC desteğini etkinleştir
        pillow_heif.register_heif_opener()
        
        self.source_folder = ""
        self.target_folder = ""
        
        self.setup_ui()
        
    def setup_ui(self):
        # Ana frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Başlık
        title_label = ttk.Label(main_frame, text="HEIC → JPG Dönüştürücü", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Kaynak klasör seçimi
        ttk.Label(main_frame, text="HEIC Dosyalarının Bulunduğu Klasör:").grid(
            row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        self.source_var = tk.StringVar()
        source_entry = ttk.Entry(main_frame, textvariable=self.source_var, width=50)
        source_entry.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        source_btn = ttk.Button(main_frame, text="Klasör Seç", 
                               command=self.select_source_folder)
        source_btn.grid(row=2, column=2, padx=(10, 0), pady=(0, 10))
        
        # Hedef klasör seçimi
        ttk.Label(main_frame, text="JPG Dosyalarının Kaydedileceği Klasör:").grid(
            row=3, column=0, sticky=tk.W, pady=(0, 5))
        
        self.target_var = tk.StringVar()
        target_entry = ttk.Entry(main_frame, textvariable=self.target_var, width=50)
        target_entry.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        target_btn = ttk.Button(main_frame, text="Klasör Seç", 
                               command=self.select_target_folder)
        target_btn.grid(row=4, column=2, padx=(10, 0), pady=(0, 10))
        
        # Kalite ayarı
        ttk.Label(main_frame, text="JPG Kalitesi (1-100):").grid(
            row=5, column=0, sticky=tk.W, pady=(10, 5))
        
        self.quality_var = tk.IntVar(value=95)
        quality_scale = ttk.Scale(main_frame, from_=1, to=100, 
                                 variable=self.quality_var, orient=tk.HORIZONTAL)
        quality_scale.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.quality_label = ttk.Label(main_frame, text="95")
        self.quality_label.grid(row=6, column=2, padx=(10, 0))
        
        # Kalite değerini güncelle
        quality_scale.configure(command=self.update_quality_label)
        
        # Dönüştür butonu
        self.convert_btn = ttk.Button(main_frame, text="Dönüştür", 
                                     command=self.start_conversion,
                                     style="Accent.TButton")
        self.convert_btn.grid(row=7, column=0, columnspan=3, pady=(20, 10))
        
        # İlerleme çubuğu
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var,
                                           maximum=100, length=400)
        self.progress_bar.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Durum etiketi
        self.status_var = tk.StringVar(value="Klasörleri seçin ve dönüştür butonuna basın")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=9, column=0, columnspan=3, pady=(0, 10))
        
        # Sonuç metni
        self.result_text = tk.Text(main_frame, height=8, width=70)
        self.result_text.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Scrollbar for text widget
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.grid(row=10, column=3, sticky=(tk.N, tk.S), pady=(10, 0))
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        # Grid configuration
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(10, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
    def update_quality_label(self, value):
        self.quality_label.config(text=str(int(float(value))))
        
    def select_source_folder(self):
        folder = filedialog.askdirectory(title="HEIC Dosyalarının Bulunduğu Klasörü Seçin")
        if folder:
            self.source_folder = folder
            self.source_var.set(folder)
            self.check_heic_files()
            
    def select_target_folder(self):
        folder = filedialog.askdirectory(title="JPG Dosyalarının Kaydedileceği Klasörü Seçin")
        if folder:
            self.target_folder = folder
            self.target_var.set(folder)
            
    def check_heic_files(self):
        if self.source_folder:
            heic_files = self.get_heic_files()
            if heic_files:
                self.status_var.set(f"{len(heic_files)} adet HEIC dosyası bulundu")
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, "Bulunan HEIC dosyaları:\n\n")
                for file in heic_files:
                    self.result_text.insert(tk.END, f"• {file}\n")
            else:
                self.status_var.set("Seçilen klasörde HEIC dosyası bulunamadı")
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, "Seçilen klasörde HEIC dosyası bulunamadı.")
                
    def get_heic_files(self):
        if not self.source_folder:
            return []
        
        heic_extensions = ['.heic', '.HEIC', '.heif', '.HEIF']
        heic_files = []
        
        for file in os.listdir(self.source_folder):
            if any(file.endswith(ext) for ext in heic_extensions):
                heic_files.append(file)
                
        return heic_files
        
    def start_conversion(self):
        if not self.source_folder:
            messagebox.showerror("Hata", "Lütfen kaynak klasörü seçin")
            return
            
        if not self.target_folder:
            messagebox.showerror("Hata", "Lütfen hedef klasörü seçin")
            return
            
        heic_files = self.get_heic_files()
        if not heic_files:
            messagebox.showerror("Hata", "Seçilen klasörde HEIC dosyası bulunamadı")
            return
            
        # Dönüştürme işlemini ayrı thread'de çalıştır
        self.convert_btn.config(state="disabled")
        conversion_thread = threading.Thread(target=self.convert_files, args=(heic_files,))
        conversion_thread.daemon = True
        conversion_thread.start()
        
    def convert_files(self, heic_files):
        total_files = len(heic_files)
        successful_conversions = 0
        failed_conversions = []
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Dönüştürme işlemi başladı...\n\n")
        
        for i, filename in enumerate(heic_files):
            try:
                # Dosya yolları
                source_path = os.path.join(self.source_folder, filename)
                name_without_ext = Path(filename).stem
                target_path = os.path.join(self.target_folder, f"{name_without_ext}.jpg")
                
                # HEIC dosyasını aç ve JPG olarak kaydet
                with Image.open(source_path) as img:
                    # RGB'ye dönüştür (HEIC bazen RGBA olabilir)
                    rgb_img = img.convert('RGB')
                    rgb_img.save(target_path, 'JPEG', quality=self.quality_var.get())
                
                successful_conversions += 1
                
                # UI güncelleme
                self.root.after(0, self.update_progress_and_status, 
                               i + 1, total_files, f"✓ {filename} → {name_without_ext}.jpg")
                
            except Exception as e:
                failed_conversions.append((filename, str(e)))
                self.root.after(0, self.update_progress_and_status, 
                               i + 1, total_files, f"✗ {filename} - Hata: {str(e)}")
        
        # İşlem tamamlandı
        self.root.after(0, self.conversion_completed, successful_conversions, failed_conversions)
        
    def update_progress_and_status(self, current, total, message):
        progress = (current / total) * 100
        self.progress_var.set(progress)
        self.status_var.set(f"İşleniyor: {current}/{total}")
        self.result_text.insert(tk.END, f"{message}\n")
        self.result_text.see(tk.END)
        
    def conversion_completed(self, successful, failed):
        self.convert_btn.config(state="normal")
        self.progress_var.set(100)
        
        summary = f"\n{'='*50}\n"
        summary += f"Dönüştürme işlemi tamamlandı!\n"
        summary += f"Başarılı: {successful} dosya\n"
        
        if failed:
            summary += f"Başarısız: {len(failed)} dosya\n\n"
            summary += "Başarısız dosyalar:\n"
            for filename, error in failed:
                summary += f"• {filename}: {error}\n"
        
        self.result_text.insert(tk.END, summary)
        self.result_text.see(tk.END)
        
        self.status_var.set(f"Tamamlandı! {successful} dosya dönüştürüldü")
        
        if successful > 0:
            messagebox.showinfo("Başarılı", 
                               f"{successful} dosya başarıyla JPG formatına dönüştürüldü!")

def main():
    try:
        import pillow_heif
    except ImportError:
        print("pillow-heif kütüphanesi bulunamadı!")
        print("Lütfen şu komutu çalıştırın: pip install pillow-heif")
        return
    
    root = tk.Tk()
    app = HEICConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()