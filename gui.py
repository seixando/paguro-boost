import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import queue
import sys
from app import SystemOptimizer


class PaguroBoostGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Paguro Boost 🦀⚡ - Otimizador de Sistema")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configurar cores estilo retro
        self.root.configure(bg='#000000')
        self.style.configure('Title.TLabel', font=('Courier', 16, 'bold'), background='#000000', foreground='#00ff00')
        self.style.configure('Subtitle.TLabel', font=('Courier', 10), background='#000000', foreground='#00aa00')
        self.style.configure('Custom.TButton', font=('Courier', 10, 'bold'))
        self.style.configure('Retro.TLabel', font=('Courier', 10), background='#000000', foreground='#00ff00')
        self.style.configure('Info.TLabel', font=('Courier', 12, 'bold'), background='#000000', foreground='#ffff00')
        
        # Inicializar otimizador
        self.optimizer = None
        self.running = False
        self.monitoring = False
        
        # Queue para comunicação entre threads
        self.log_queue = queue.Queue()
        
        self.create_widgets()
        self.process_log_queue()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Título estilo retro
        title_text = """
 ____                            ____                    _   
|  _ \\ __ _  __ _ _   _ _ __ ___  | __ )  ___   ___  ___ | |_ 
| |_) / _` |/ _` | | | | '__/ _ \\|  _ \\ / _ \\ / _ \\/ __|| __|
|  __/ (_| | (_| | |_| | | | (_) | |_) | (_) | (_) \\__ \\| |_ 
|_|   \\__,_|\\__, |\\__,_|_|  \\___/|____/ \\___/ \\___/|___/ \\__|
            |___/                                           
        """
        title_label = ttk.Label(main_frame, text=title_text, style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 5))
        
        subtitle_label = ttk.Label(main_frame, text=">>> SISTEMA DE OTIMIZAÇÃO CROSS-PLATFORM <<<", style='Subtitle.TLabel')
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Frame de informações do sistema com visual retro
        info_frame = ttk.LabelFrame(main_frame, text="[STATUS DO SISTEMA]", padding="10")
        info_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(0, weight=1)
        
        # Canvas para gráficos retro
        self.status_canvas = tk.Canvas(info_frame, height=120, bg='#000000', highlightthickness=0)
        self.status_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Labels de informação estilo retro
        self.os_label = ttk.Label(info_frame, text="SISTEMA: DETECTANDO...", style='Retro.TLabel')
        self.os_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Frame de controles
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)
        control_frame.columnconfigure(2, weight=1)
        
        # Botões de ação
        self.start_button = ttk.Button(control_frame, text=">> Otimização Completa", 
                                      command=self.start_optimization, style='Custom.TButton')
        self.start_button.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        
        self.refresh_button = ttk.Button(control_frame, text="[!] Atualizar Info", 
                                        command=self.refresh_system_info, style='Custom.TButton')
        self.refresh_button.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        self.memory_analysis_button = ttk.Button(control_frame, text="[M] Análise RAM", 
                                               command=self.show_memory_analysis, style='Custom.TButton')
        self.memory_analysis_button.grid(row=1, column=0, padx=(0, 5), pady=(5, 0), sticky=(tk.W, tk.E))
        
        self.performance_report_button = ttk.Button(control_frame, text="[R] Relatório Performance", 
                                                  command=self.show_performance_report, style='Custom.TButton')
        self.performance_report_button.grid(row=1, column=1, padx=5, pady=(5, 0), sticky=(tk.W, tk.E))
        
        self.disk_analysis_button = ttk.Button(control_frame, text="[D] Análise Disco", 
                                             command=self.show_disk_analysis, style='Custom.TButton')
        self.disk_analysis_button.grid(row=2, column=0, padx=(0, 5), pady=(5, 0), sticky=(tk.W, tk.E))
        
        self.monitor_toggle_button = ttk.Button(control_frame, text="[>] Iniciar Monitor", 
                                              command=self.toggle_monitoring, style='Custom.TButton')
        self.monitor_toggle_button.grid(row=1, column=2, padx=(5, 0), pady=(5, 0), sticky=(tk.W, tk.E))
        
        self.stop_button = ttk.Button(control_frame, text="[X] Parar", 
                                     command=self.stop_optimization, style='Custom.TButton', 
                                     state='disabled')
        self.stop_button.grid(row=0, column=2, padx=(5, 0), sticky=(tk.W, tk.E))
        
        # Frame de opções avançadas
        options_frame = ttk.LabelFrame(main_frame, text="Opções de Otimização", padding="5")
        options_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))
        
        # Checkboxes para operações
        self.clean_temp_var = tk.BooleanVar(value=True)
        self.clean_cache_var = tk.BooleanVar(value=True)
        self.optimize_ram_var = tk.BooleanVar(value=True)
        self.update_packages_var = tk.BooleanVar(value=True)
        self.check_integrity_var = tk.BooleanVar(value=True)
        self.scan_virus_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(options_frame, text="[T] Limpar Temporários", 
                       variable=self.clean_temp_var).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="[C] Limpar Cache", 
                       variable=self.clean_cache_var).grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="[M] Otimizar RAM", 
                       variable=self.optimize_ram_var).grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="[U] Atualizar Pacotes", 
                       variable=self.update_packages_var).grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="[I] Verificar Integridade", 
                       variable=self.check_integrity_var).grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="[V] Scan de Vírus", 
                       variable=self.scan_virus_var).grid(row=5, column=0, sticky=tk.W, pady=2)
        
        self.disk_optimization_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="[D] Otimizar Disco", 
                       variable=self.disk_optimization_var).grid(row=6, column=0, sticky=tk.W, pady=2)
        
        # Log de saída estilo terminal retro
        log_frame = ttk.LabelFrame(main_frame, text="[TERMINAL DE OPERAÇÕES]", padding="5")
        log_frame.grid(row=4, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=50, 
                                                 wrap=tk.WORD, font=('Courier', 9),
                                                 bg='#000000', fg='#00ff00',
                                                 insertbackground='#00ff00',
                                                 selectbackground='#00aa00')
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Adicionar mensagem de boas-vindas estilo terminal
        welcome_msg = """
┌─────────────────────────────────────────────────┐
│          PAGURO BOOST TERMINAL v2.0             │
│                                                 │
│  Sistema pronto para otimização...              │
│  Digite comandos ou use a interface gráfica     │
└─────────────────────────────────────────────────┘

[SYSTEM] Terminal inicializado com sucesso.
[READY] Aguardando comandos...

"""
        self.log_text.insert(tk.END, welcome_msg)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Inicializar informações do sistema
        self.refresh_system_info()
        
        # Iniciar atualização contínua dos gráficos
        self.update_retro_display()
        
    def log_message(self, message):
        """Adiciona mensagem ao log de forma thread-safe."""
        import time
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_queue.put(formatted_message)
        
    def process_log_queue(self):
        """Processa mensagens do queue de log."""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)
                self.root.update_idletasks()
        except queue.Empty:
            pass
        
        # Reagendar para próxima verificação
        self.root.after(100, self.process_log_queue)
        
    def refresh_system_info(self):
        """Atualiza informações do sistema."""
        def update_info():
            try:
                if not self.optimizer:
                    self.optimizer = SystemOptimizer()
                
                # Detectar sistema
                import platform
                is_wsl = 'microsoft' in platform.uname().release.lower()
                os_info = f"{platform.system()} {'(WSL)' if is_wsl else ''}"
                
                # Obter métricas
                cpu, memory, disk = self.optimizer.medir_uso_recursos()
                
                # Atualizar labels na thread principal
                self.root.after(0, lambda: self.os_label.config(text=f"SISTEMA: {os_info.upper()}"))
                
            except Exception as e:
                self.log_message(f"Erro ao atualizar informações: {e}")
        
        # Executar em thread separada
        threading.Thread(target=update_info, daemon=True).start()
        
    def create_ascii_bar(self, percentage, width=20):
        """Cria barra de progresso ASCII."""
        filled = int((percentage / 100) * width)
        empty = width - filled
        
        if percentage >= 80:
            fill_char = '█'
            color = '#ff0000'  # Vermelho para crítico
        elif percentage >= 60:
            fill_char = '▓'
            color = '#ffaa00'  # Laranja para alto
        else:
            fill_char = '▒'
            color = '#00ff00'  # Verde para normal
            
        bar = fill_char * filled + '░' * empty
        return bar, color
    
    def update_retro_display(self):
        """Atualiza display retro com métricas em tempo real."""
        try:
            if not self.optimizer:
                self.optimizer = SystemOptimizer()
            
            # Obter métricas atuais
            cpu, memory, disk = self.optimizer.medir_uso_recursos()
            
            # Limpar canvas
            self.status_canvas.delete("all")
            
            # Configurações do canvas
            canvas_width = self.status_canvas.winfo_width()
            if canvas_width <= 1:  # Canvas ainda não foi renderizado
                canvas_width = 600
            
            # Título do monitor
            self.status_canvas.create_text(canvas_width//2, 15, text="MONITOR DE RECURSOS DO SISTEMA", 
                                         fill='#00ff00', font=('Courier', 12, 'bold'))
            
            # Linha de separação
            self.status_canvas.create_line(10, 25, canvas_width-10, 25, fill='#00aa00', width=2)
            
            # CPU
            cpu_bar, cpu_color = self.create_ascii_bar(cpu)
            self.status_canvas.create_text(15, 45, text=f"CPU:", fill='#00ff00', 
                                         font=('Courier', 10, 'bold'), anchor='w')
            self.status_canvas.create_text(60, 45, text=f"[{cpu_bar}]", fill=cpu_color, 
                                         font=('Courier', 10), anchor='w')
            self.status_canvas.create_text(canvas_width-80, 45, text=f"{cpu:5.1f}%", fill='#ffff00', 
                                         font=('Courier', 10, 'bold'), anchor='w')
            
            # Memória
            mem_bar, mem_color = self.create_ascii_bar(memory)
            self.status_canvas.create_text(15, 65, text=f"RAM:", fill='#00ff00', 
                                         font=('Courier', 10, 'bold'), anchor='w')
            self.status_canvas.create_text(60, 65, text=f"[{mem_bar}]", fill=mem_color, 
                                         font=('Courier', 10), anchor='w')
            self.status_canvas.create_text(canvas_width-80, 65, text=f"{memory:5.1f}%", fill='#ffff00', 
                                         font=('Courier', 10, 'bold'), anchor='w')
            
            # Disco
            disk_bar, disk_color = self.create_ascii_bar(disk)
            self.status_canvas.create_text(15, 85, text=f"HDD:", fill='#00ff00', 
                                         font=('Courier', 10, 'bold'), anchor='w')
            self.status_canvas.create_text(60, 85, text=f"[{disk_bar}]", fill=disk_color, 
                                         font=('Courier', 10), anchor='w')
            self.status_canvas.create_text(canvas_width-80, 85, text=f"{disk:5.1f}%", fill='#ffff00', 
                                         font=('Courier', 10, 'bold'), anchor='w')
            
            # Status geral
            if max(cpu, memory, disk) >= 80:
                status_text = "CRÍTICO"
                status_color = '#ff0000'
            elif max(cpu, memory, disk) >= 60:
                status_text = "ALTO"
                status_color = '#ffaa00'
            else:
                status_text = "NORMAL"
                status_color = '#00ff00'
                
            self.status_canvas.create_text(canvas_width-15, 105, text=f"STATUS: {status_text}", 
                                         fill=status_color, font=('Courier', 10, 'bold'), anchor='e')
            
            # Linha de separação inferior
            self.status_canvas.create_line(10, 95, canvas_width-10, 95, fill='#00aa00', width=1)
            
        except Exception as e:
            print(f"Erro ao atualizar display retro: {e}")
        
        # Reagendar para próxima atualização (2 segundos)
        self.root.after(2000, self.update_retro_display)
        
    def start_optimization(self):
        """Inicia o processo de otimização."""
        if self.running:
            return
            
        self.running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress.start()
        
        # Limpar log
        self.log_text.delete(1.0, tk.END)
        self.log_message("=== Iniciando Otimização do Sistema ===")
        
        # Executar otimização em thread separada
        optimization_thread = threading.Thread(target=self.run_optimization, daemon=True)
        optimization_thread.start()
        
    def run_optimization(self):
        """Executa a otimização em thread separada."""
        try:
            if not self.optimizer:
                self.optimizer = SystemOptimizer()
            
            # Verificar gerenciador de pacotes
            if not self.optimizer.verificar_gerenciador_pacotes():
                self.log_message("[!] Gerenciador de pacotes não disponível!")
                return
            
            # Medições iniciais
            self.log_message("[M] Medindo recursos iniciais...")
            cpu_initial, mem_initial, disk_initial = self.optimizer.medir_uso_recursos()
            self.log_message(f"CPU: {cpu_initial:.1f}% | Memória: {mem_initial:.1f}% | Disco: {disk_initial:.1f}%")
            
            # Executar operações selecionadas
            operations = []
            
            if self.clean_temp_var.get():
                operations.append((self.optimizer.limpar_temporarios, "[T] Limpando arquivos temporários"))
                
            if self.clean_cache_var.get():
                operations.append((self.optimizer.limpar_cache_sistema, "[C] Limpando cache do sistema"))
                
            if self.optimize_ram_var.get():
                operations.append((self.optimizer.otimizar_memoria_ram, "[M] Otimizando memória RAM"))
                
            if self.update_packages_var.get():
                operations.append((self.optimizer.atualizar_pacotes, "[U] Atualizando pacotes"))
                
            if self.check_integrity_var.get():
                operations.append((self.optimizer.verificar_integridade, "[I] Verificando integridade"))
                
            if self.scan_virus_var.get():
                operations.append((self.optimizer.verificar_virus, "[V] Executando scan de vírus"))
                
            if self.disk_optimization_var.get():
                operations.append((lambda: self.optimizer.otimizar_disco_avancado(limpar_antigos=True), "[D] Otimizando disco avançado"))
            
            # Executar operações
            for operation, description in operations:
                if not self.running:  # Verificar se foi cancelado
                    break
                    
                self.log_message(description)
                try:
                    success = operation()
                    status = "[OK] Concluído" if success else "[!] Com avisos"
                    self.log_message(f"{description} - {status}")
                except Exception as e:
                    self.log_message(f"{description} - [ERR] Erro: {e}")
            
            # Medições finais
            if self.running:
                self.log_message("[M] Medindo recursos finais...")
                cpu_final, mem_final, disk_final = self.optimizer.medir_uso_recursos()
                
                self.log_message("=== Relatório Final ===")
                self.log_message(f"CPU: {cpu_initial:.1f}% -> {cpu_final:.1f}% (D{cpu_initial-cpu_final:+.1f}%)")
                self.log_message(f"RAM: {mem_initial:.1f}% -> {mem_final:.1f}% (D{mem_initial-mem_final:+.1f}%)")
                self.log_message(f"Disco: {disk_initial:.1f}% -> {disk_final:.1f}% (D{disk_initial-disk_final:+.1f}%)")
                self.log_message("[!] Recomendação: Reinicie o sistema para melhor performance.")
                
        except Exception as e:
            self.log_message(f"[ERR] Erro fatal na otimização: {e}")
        finally:
            # Finalizar
            self.root.after(0, self.finish_optimization)
            
    def stop_optimization(self):
        """Para a otimização."""
        self.running = False
        self.log_message("[X] Operação cancelada pelo usuário.")
        
    def finish_optimization(self):
        """Finaliza a otimização e restaura interface."""
        self.running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress.stop()
        
        # Atualizar informações do sistema
        self.refresh_system_info()
        
    def show_memory_analysis(self):
        """Mostra janela com análise detalhada de memória."""
        def analyze_memory():
            try:
                if not self.optimizer:
                    self.optimizer = SystemOptimizer()
                
                analysis = self.optimizer.analisar_uso_memoria_detalhado()
                
                # Criar janela de análise
                analysis_window = tk.Toplevel(self.root)
                analysis_window.title("Análise Detalhada de Memória")
                analysis_window.geometry("600x500")
                analysis_window.resizable(True, True)
                
                # Frame principal
                main_frame = ttk.Frame(analysis_window, padding="20")
                main_frame.pack(fill=tk.BOTH, expand=True)
                
                # Informações gerais
                info_frame = ttk.LabelFrame(main_frame, text="Informações Gerais", padding="10")
                info_frame.pack(fill=tk.X, pady=(0, 10))
                
                ttk.Label(info_frame, text=f"Memória Total: {analysis.get('memoria_total_gb', 0)} GB", 
                         font=('Arial', 10, 'bold')).pack(anchor=tk.W)
                ttk.Label(info_frame, text=f"Memória Usada: {analysis.get('memoria_usada_gb', 0)} GB", 
                         font=('Arial', 10)).pack(anchor=tk.W)
                ttk.Label(info_frame, text=f"Memória Livre: {analysis.get('memoria_livre_gb', 0)} GB", 
                         font=('Arial', 10)).pack(anchor=tk.W)
                ttk.Label(info_frame, text=f"Uso Percentual: {analysis.get('percentual_uso', 0):.1f}%", 
                         font=('Arial', 10, 'bold')).pack(anchor=tk.W)
                
                if analysis.get('swap_total_gb', 0) > 0:
                    ttk.Label(info_frame, text=f"Swap Total: {analysis.get('swap_total_gb', 0)} GB").pack(anchor=tk.W)
                    ttk.Label(info_frame, text=f"Swap Usado: {analysis.get('swap_usado_gb', 0)} GB").pack(anchor=tk.W)
                
                # Top processos
                proc_frame = ttk.LabelFrame(main_frame, text="Top 10 Processos (Memória)", padding="10")
                proc_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
                
                # Treeview para processos
                tree = ttk.Treeview(proc_frame, columns=('PID', 'Memória %', 'MB'), show='tree headings')
                tree.heading('#0', text='Processo')
                tree.heading('PID', text='PID')
                tree.heading('Memória %', text='Memória %')
                tree.heading('MB', text='MB')
                
                tree.column('#0', width=200)
                tree.column('PID', width=80)
                tree.column('Memória %', width=100)
                tree.column('MB', width=100)
                
                for proc in analysis.get('processos_top_memoria', []):
                    tree.insert('', tk.END, text=proc['name'], 
                               values=(proc['pid'], f"{proc['memory_percent']:.1f}%", proc['memory_mb']))
                
                # Scrollbar para treeview
                scrollbar = ttk.Scrollbar(proc_frame, orient=tk.VERTICAL, command=tree.yview)
                tree.configure(yscrollcommand=scrollbar.set)
                
                tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                # Recomendações
                rec_frame = ttk.LabelFrame(main_frame, text="Recomendações", padding="10")
                rec_frame.pack(fill=tk.X)
                
                for rec in analysis.get('recomendacoes', []):
                    ttk.Label(rec_frame, text=rec, font=('Arial', 9)).pack(anchor=tk.W, pady=2)
                
                if not analysis.get('recomendacoes'):
                    ttk.Label(rec_frame, text="[OK] Uso de memória está otimizado!", 
                             font=('Arial', 10, 'bold'), foreground='green').pack(anchor=tk.W)
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro na análise de memória: {e}")
        
        # Executar análise em thread separada
        threading.Thread(target=analyze_memory, daemon=True).start()
        
    def show_performance_report(self):
        """Mostra janela com relatório de performance."""
        def generate_report():
            try:
                if not self.optimizer:
                    self.optimizer = SystemOptimizer()
                
                # Permitir escolha do período
                period_window = tk.Toplevel(self.root)
                period_window.title("Período do Relatório")
                period_window.geometry("300x200")
                period_window.resizable(False, False)
                
                # Centralizar janela
                period_window.transient(self.root)
                period_window.grab_set()
                
                ttk.Label(period_window, text="Selecione o período:", font=('Arial', 12, 'bold')).pack(pady=10)
                
                period_var = tk.IntVar(value=24)
                
                ttk.Radiobutton(period_window, text="Últimas 6 horas", variable=period_var, value=6).pack(pady=5)
                ttk.Radiobutton(period_window, text="Últimas 24 horas", variable=period_var, value=24).pack(pady=5)
                ttk.Radiobutton(period_window, text="Últimos 3 dias", variable=period_var, value=72).pack(pady=5)
                ttk.Radiobutton(period_window, text="Última semana", variable=period_var, value=168).pack(pady=5)
                
                def generate_with_period():
                    hours = period_var.get()
                    period_window.destroy()
                    
                    # Gerar relatório
                    report = self.optimizer.gerar_relatorio_performance(hours)
                    
                    if 'error' in report:
                        messagebox.showwarning("Aviso", report['error'])
                        return
                    
                    # Criar janela do relatório
                    report_window = tk.Toplevel(self.root)
                    report_window.title(f"Relatório de Performance - {report.get('period', 'N/A')}")
                    report_window.geometry("800x600")
                    report_window.resizable(True, True)
                    
                    # Frame principal com scrollbar
                    main_frame = ttk.Frame(report_window)
                    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
                    
                    # Canvas e scrollbar
                    canvas = tk.Canvas(main_frame)
                    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
                    scrollable_frame = ttk.Frame(canvas)
                    
                    scrollable_frame.bind(
                        "<Configure>",
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                    )
                    
                    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                    canvas.configure(yscrollcommand=scrollbar.set)
                    
                    # Título
                    ttk.Label(scrollable_frame, text="[R] RELATÓRIO DE PERFORMANCE", 
                             font=('Arial', 16, 'bold')).pack(pady=(0, 20))
                    
                    # Informações básicas
                    info_frame = ttk.LabelFrame(scrollable_frame, text="Informações Gerais", padding="10")
                    info_frame.pack(fill=tk.X, pady=(0, 10))
                    
                    ttk.Label(info_frame, text=f"Período: {report.get('period', 'N/A')}", 
                             font=('Arial', 10, 'bold')).pack(anchor=tk.W)
                    ttk.Label(info_frame, text=f"Amostras coletadas: {report.get('sample_count', 0)}").pack(anchor=tk.W)
                    ttk.Label(info_frame, text=f"Gerado em: {report.get('generated_at', 'N/A')[:19]}").pack(anchor=tk.W)
                    
                    # Médias
                    averages = report.get('averages', {}).get('averages', {})
                    if averages:
                        avg_frame = ttk.LabelFrame(scrollable_frame, text="Médias do Período", padding="10")
                        avg_frame.pack(fill=tk.X, pady=(0, 10))
                        
                        ttk.Label(avg_frame, text=f"CPU Média: {averages.get('cpu_percent', 0):.1f}%", 
                                 font=('Arial', 10)).pack(anchor=tk.W)
                        ttk.Label(avg_frame, text=f"Memória Média: {averages.get('memory_percent', 0):.1f}%", 
                                 font=('Arial', 10)).pack(anchor=tk.W)
                        ttk.Label(avg_frame, text=f"Disco Médio: {averages.get('disk_percent', 0):.1f}%", 
                                 font=('Arial', 10)).pack(anchor=tk.W)
                    
                    # Picos
                    peaks = report.get('averages', {}).get('peaks', {})
                    if peaks:
                        peaks_frame = ttk.LabelFrame(scrollable_frame, text="Picos de Uso", padding="10")
                        peaks_frame.pack(fill=tk.X, pady=(0, 10))
                        
                        ttk.Label(peaks_frame, text=f"CPU Máxima: {peaks.get('cpu_max', 0):.1f}%", 
                                 font=('Arial', 10)).pack(anchor=tk.W)
                        ttk.Label(peaks_frame, text=f"Memória Máxima: {peaks.get('memory_max', 0):.1f}%", 
                                 font=('Arial', 10)).pack(anchor=tk.W)
                        ttk.Label(peaks_frame, text=f"Disco Máximo: {peaks.get('disk_max', 0):.1f}%", 
                                 font=('Arial', 10)).pack(anchor=tk.W)
                    
                    # Estabilidade
                    stability = report.get('stability', {})
                    if stability:
                        stab_frame = ttk.LabelFrame(scrollable_frame, text="Análise de Estabilidade", padding="10")
                        stab_frame.pack(fill=tk.X, pady=(0, 10))
                        
                        ttk.Label(stab_frame, text=f"Score de Estabilidade: {stability.get('stability_score', 'N/A')}", 
                                 font=('Arial', 12, 'bold')).pack(anchor=tk.W)
                        ttk.Label(stab_frame, text=f"Variância CPU: {stability.get('cpu_variance', 0):.2f}", 
                                 font=('Arial', 10)).pack(anchor=tk.W)
                        ttk.Label(stab_frame, text=f"Variância Memória: {stability.get('memory_variance', 0):.2f}", 
                                 font=('Arial', 10)).pack(anchor=tk.W)
                    
                    # Padrões
                    patterns = report.get('patterns', {})
                    if patterns:
                        pattern_frame = ttk.LabelFrame(scrollable_frame, text="Padrões de Uso", padding="10")
                        pattern_frame.pack(fill=tk.X, pady=(0, 10))
                        
                        trend = patterns.get('usage_trend', 'N/A')
                        ttk.Label(pattern_frame, text=f"Tendência de Uso: {trend}", 
                                 font=('Arial', 10, 'bold')).pack(anchor=tk.W)
                        
                        peak_hours = patterns.get('peak_hours', {})
                        if peak_hours:
                            ttk.Label(pattern_frame, text=f"Pico CPU: {peak_hours.get('cpu_peak_hour', 0)}:00h ({peak_hours.get('cpu_peak_value', 0):.1f}%)", 
                                     font=('Arial', 10)).pack(anchor=tk.W)
                            ttk.Label(pattern_frame, text=f"Pico Memória: {peak_hours.get('memory_peak_hour', 0)}:00h ({peak_hours.get('memory_peak_value', 0):.1f}%)", 
                                     font=('Arial', 10)).pack(anchor=tk.W)
                    
                    # Recomendações
                    recommendations = report.get('recommendations', [])
                    if recommendations:
                        rec_frame = ttk.LabelFrame(scrollable_frame, text="Recomendações", padding="10")
                        rec_frame.pack(fill=tk.X, pady=(0, 10))
                        
                        for rec in recommendations:
                            ttk.Label(rec_frame, text=rec, font=('Arial', 10), wraplength=750).pack(anchor=tk.W, pady=2)
                    
                    # Configurar scrollbar
                    canvas.pack(side="left", fill="both", expand=True)
                    scrollbar.pack(side="right", fill="y")
                
                ttk.Button(period_window, text="Gerar Relatório", command=generate_with_period).pack(pady=20)
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao gerar relatório: {e}")
        
        # Executar em thread separada
        threading.Thread(target=generate_report, daemon=True).start()
    
    def toggle_monitoring(self):
        """Alterna monitoramento contínuo."""
        if not self.optimizer:
            self.optimizer = SystemOptimizer()
        
        if not self.monitoring:
            # Iniciar monitoramento
            if self.optimizer.iniciar_monitoramento_continuo(30):
                self.monitoring = True
                self.monitor_toggle_button.config(text="[||] Parar Monitor")
                self.log_message("[>] Monitoramento contínuo iniciado (30s intervalos)")
            else:
                messagebox.showerror("Erro", "Não foi possível iniciar o monitoramento")
        else:
            # Parar monitoramento
            self.optimizer.parar_monitoramento_continuo()
            self.monitoring = False
            self.monitor_toggle_button.config(text="[>] Iniciar Monitor")
            self.log_message("[||] Monitoramento contínuo parado")
    
    def show_disk_analysis(self):
        """Mostra janela com análise detalhada de disco."""
        def analyze_disk():
            try:
                if not self.optimizer:
                    self.optimizer = SystemOptimizer()
                
                analysis = self.optimizer.analisar_uso_disco_detalhado()
                
                if not analysis:
                    messagebox.showerror("Erro", "Não foi possível analisar o disco")
                    return
                
                # Criar janela de análise
                analysis_window = tk.Toplevel(self.root)
                analysis_window.title("Análise Detalhada de Disco")
                analysis_window.geometry("700x600")
                analysis_window.resizable(True, True)
                
                # Frame principal com scrollbar
                main_frame = ttk.Frame(analysis_window)
                main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
                
                # Canvas e scrollbar
                canvas = tk.Canvas(main_frame)
                scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
                scrollable_frame = ttk.Frame(canvas)
                
                scrollable_frame.bind(
                    "<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                )
                
                canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)
                
                # Título
                ttk.Label(scrollable_frame, text="[D] ANÁLISE DE DISCO", 
                         font=('Courier', 16, 'bold')).pack(pady=(0, 20))
                
                # Informações gerais
                info_frame = ttk.LabelFrame(scrollable_frame, text="Informações Gerais", padding="10")
                info_frame.pack(fill=tk.X, pady=(0, 10))
                
                ttk.Label(info_frame, text=f"Caminho: {analysis.get('caminho', 'N/A')}", 
                         font=('Courier', 10, 'bold')).pack(anchor=tk.W)
                ttk.Label(info_frame, text=f"Espaço Total: {analysis.get('espaco_total_gb', 0)} GB").pack(anchor=tk.W)
                ttk.Label(info_frame, text=f"Espaço Usado: {analysis.get('espaco_usado_gb', 0)} GB").pack(anchor=tk.W)
                ttk.Label(info_frame, text=f"Espaço Livre: {analysis.get('espaco_livre_gb', 0)} GB").pack(anchor=tk.W)
                ttk.Label(info_frame, text=f"Uso Percentual: {analysis.get('percentual_uso', 0):.1f}%", 
                         font=('Courier', 10, 'bold')).pack(anchor=tk.W)
                
                # Diretórios grandes
                dirs_grandes = analysis.get('diretorios_grandes', [])
                if dirs_grandes:
                    dirs_frame = ttk.LabelFrame(scrollable_frame, text="Diretórios Grandes", padding="10")
                    dirs_frame.pack(fill=tk.X, pady=(0, 10))
                    
                    for i, diretorio in enumerate(dirs_grandes[:5]):  # Top 5
                        nome = os.path.basename(diretorio['caminho']) or diretorio['caminho']
                        ttk.Label(dirs_frame, text=f"{i+1}. {nome}: {diretorio['tamanho_gb']:.1f} GB", 
                                 font=('Courier', 9)).pack(anchor=tk.W)
                
                # Tipos de arquivo
                tipos = analysis.get('tipos_arquivo', {})
                if tipos:
                    tipos_frame = ttk.LabelFrame(scrollable_frame, text="Tipos de Arquivo (Sample)", padding="10")
                    tipos_frame.pack(fill=tk.X, pady=(0, 10))
                    
                    for ext, data in list(tipos.items())[:10]:  # Top 10
                        ttk.Label(tipos_frame, text=f"{ext}: {data['arquivos']} arquivos ({data['tamanho_mb']:.1f} MB)", 
                                 font=('Courier', 9)).pack(anchor=tk.W)
                
                # Arquivos antigos
                antigos = analysis.get('arquivos_antigos', {})
                if antigos and antigos.get('total_arquivos', 0) > 0:
                    antigos_frame = ttk.LabelFrame(scrollable_frame, text="Arquivos Antigos", padding="10")
                    antigos_frame.pack(fill=tk.X, pady=(0, 10))
                    
                    ttk.Label(antigos_frame, text=f"Total: {antigos['total_arquivos']} arquivos", 
                             font=('Courier', 10, 'bold')).pack(anchor=tk.W)
                    ttk.Label(antigos_frame, text=f"Tamanho: {antigos['tamanho_total_mb']:.1f} MB").pack(anchor=tk.W)
                    
                    sample_arquivos = antigos.get('sample_arquivos', [])
                    for arquivo in sample_arquivos[:3]:  # Top 3
                        nome = os.path.basename(arquivo['arquivo'])
                        ttk.Label(antigos_frame, text=f"• {nome}: {arquivo['tamanho_mb']:.1f} MB ({arquivo['dias_antigo']} dias)", 
                                 font=('Courier', 9)).pack(anchor=tk.W, padx=(10, 0))
                
                # Duplicados
                duplicados = analysis.get('duplicados_sample', {})
                if duplicados and duplicados.get('grupos_duplicados', 0) > 0:
                    dup_frame = ttk.LabelFrame(scrollable_frame, text="Arquivos Duplicados (Sample)", padding="10")
                    dup_frame.pack(fill=tk.X, pady=(0, 10))
                    
                    ttk.Label(dup_frame, text=f"Grupos de duplicados: {duplicados['grupos_duplicados']}", 
                             font=('Courier', 10, 'bold')).pack(anchor=tk.W)
                    ttk.Label(dup_frame, text=f"Espaço desperdiçado: {duplicados['tamanho_desperdicado_mb']:.1f} MB").pack(anchor=tk.W)
                
                # Recomendações
                recomendacoes = analysis.get('recomendacoes', [])
                if recomendacoes:
                    rec_frame = ttk.LabelFrame(scrollable_frame, text="Recomendações", padding="10")
                    rec_frame.pack(fill=tk.X)
                    
                    for rec in recomendacoes:
                        ttk.Label(rec_frame, text=rec, font=('Courier', 9), wraplength=650).pack(anchor=tk.W, pady=2)
                
                # Configurar scrollbar
                canvas.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro na análise de disco: {e}")
        
        # Executar análise em thread separada
        threading.Thread(target=analyze_disk, daemon=True).start()


def main():
    root = tk.Tk()
    app = PaguroBoostGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()