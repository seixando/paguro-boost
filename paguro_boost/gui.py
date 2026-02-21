import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import queue
import time
import os
import sys

# Attempt to import SystemOptimizer, handle running directly vs package
try:
    from .app import SystemOptimizer
except ImportError:
    from app import SystemOptimizer

# Configuração Base do CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class ProcessLogText(ctk.CTkTextbox):
    """Terminal Retro Customizado"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(
            font=ctk.CTkFont(family="Courier", size=12),
            text_color="#00ff00",
            fg_color="#050505",
            border_color="#00ff00",
            border_width=1,
            wrap="word"
        )

class PaguroBoostGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração da Janela
        self.title("Paguro Boost 🦀⚡ - Premium Otimizador")
        self.geometry("950x650")
        self.minsize(850, 600)
        
        # Paleta Retro-Hacker Premium
        self.colors = {
            "bg": "#050505",
            "surface": "#111111",
            "accent": "#00ff00",
            "accent_hover": "#00cc00",
            "text": "#00ff00",
            "text_dim": "#00aa00",
            "warning": "#ffaa00",
            "critical": "#ff0000"
        }
        self.configure(fg_color=self.colors["bg"])

        # Grid Base -> 1 linha, 2 colunas (Sidebar e Principal)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Estados e Backend
        self.optimizer = None
        self.running = False
        self.monitoring = False
        self.log_queue = queue.Queue()

        # Componentes Principais
        self.create_sidebar()
        self.create_main_frames()

        # Iniciar interface e rotinas
        self.select_frame_by_name("dashboard")
        self.process_log_queue()
        self.refresh_system_info()
        self.update_retro_display()

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=self.colors["surface"])
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        # Logo / Título
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="PAGURO\nBOOST ⚡", 
            font=ctk.CTkFont(family="Courier", size=24, weight="bold"),
            text_color=self.colors["accent"]
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 30))

        # Botões de Navegação
        self.nav_btns = {}
        
        btn_configs = [
            ("dashboard", "📊 Dashboard"),
            ("optimizer", "⚡ Otimizador"),
            ("analysis", "🔍 Análises Gerais")
        ]

        for idx, (name, text) in enumerate(btn_configs, start=1):
            btn = ctk.CTkButton(
                self.sidebar_frame, text=text,
                font=ctk.CTkFont(family="Courier", size=14, weight="bold"),
                fg_color="transparent", text_color=self.colors["text"],
                hover_color=self.colors["surface"], anchor="w",
                command=lambda n=name: self.select_frame_by_name(n)
            )
            btn.grid(row=idx, column=0, padx=10, pady=10, sticky="ew")
            self.nav_btns[name] = btn

        # Info de Sistema no Rodapé do Sidebar
        self.os_label = ctk.CTkLabel(
            self.sidebar_frame, text="SISTEMA:\nDETECTANDO...", 
            font=ctk.CTkFont(family="Courier", size=12),
            text_color=self.colors["text_dim"]
        )
        self.os_label.grid(row=6, column=0, padx=20, pady=20, sticky="s")


    def create_main_frames(self):
        self.frames = {}
        
        # --- FRAME 1: Dashboard ---
        self.frames["dashboard"] = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frames["dashboard"].grid_columnconfigure(0, weight=1)
        self.frames["dashboard"].grid_rowconfigure(1, weight=1)
        
        # Título
        ctk.CTkLabel(
            self.frames["dashboard"], text=">>> MONITOR DO SISTEMA <<<",
            font=ctk.CTkFont(family="Courier", size=20, weight="bold"),
            text_color=self.colors["accent"]
        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nw")

        # Container dos Gráficos
        self.monitor_frame = ctk.CTkFrame(self.frames["dashboard"], fg_color=self.colors["surface"], corner_radius=10)
        self.monitor_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.monitor_frame.grid_columnconfigure(1, weight=1)
        
        # Barras de Progresso
        self.progress_bars = {}
        self.progress_labels = {}
        
        resources = [("CPU", 0), ("RAM", 1), ("HDD", 2)]
        for label, row in resources:
            title = ctk.CTkLabel(self.monitor_frame, text=f"{label}:", font=ctk.CTkFont(family="Courier", size=16, weight="bold"), text_color=self.colors["accent"])
            title.grid(row=row, column=0, padx=(20, 10), pady=30, sticky="w")
            
            pbar = ctk.CTkProgressBar(self.monitor_frame, height=20, progress_color=self.colors["accent"], fg_color="#222222")
            pbar.grid(row=row, column=1, padx=10, pady=30, sticky="ew")
            pbar.set(0)
            
            value_label = ctk.CTkLabel(self.monitor_frame, text="0.0%", font=ctk.CTkFont(family="Courier", size=16, weight="bold"), text_color=self.colors["accent"])
            value_label.grid(row=row, column=2, padx=(10, 20), pady=30, sticky="e")
            
            self.progress_bars[label.lower()] = pbar
            self.progress_labels[label.lower()] = value_label
            
        # Controles do Monitor
        monitor_ctrls = ctk.CTkFrame(self.frames["dashboard"], fg_color="transparent")
        monitor_ctrls.grid(row=2, column=0, padx=20, pady=20, sticky="e")
        
        self.monitor_btn = ctk.CTkButton(
            monitor_ctrls, text="[>] INICIAR MONITOR LOG", 
            font=ctk.CTkFont(family="Courier", size=14, weight="bold"),
            fg_color=self.colors["surface"], hover_color="#2a2a2a",
            border_color=self.colors["accent"], border_width=1,
            command=self.toggle_monitoring
        )
        self.monitor_btn.pack(side="right", padx=10)

        ctk.CTkButton(
            monitor_ctrls, text="[!] ATUALIZAR", 
            font=ctk.CTkFont(family="Courier", size=14, weight="bold"),
            fg_color=self.colors["surface"], hover_color="#2a2a2a",
            border_color=self.colors["accent"], border_width=1,
            command=self.refresh_system_info
        ).pack(side="right")


        # --- FRAME 2: Otimizador ---
        self.frames["optimizer"] = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frames["optimizer"].grid_columnconfigure((0, 1), weight=1)
        self.frames["optimizer"].grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self.frames["optimizer"], text=">>> TERMINAL DE OTIMIZAÇÃO <<<",
            font=ctk.CTkFont(family="Courier", size=20, weight="bold"),
            text_color=self.colors["accent"]
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="nw")

        # Painel de Opções
        options_panel = ctk.CTkFrame(self.frames["optimizer"], fg_color=self.colors["surface"], corner_radius=10)
        options_panel.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="nsew")
        
        ctk.CTkLabel(options_panel, text="OPÇÕES DE TASK", font=ctk.CTkFont(family="Courier", size=14, weight="bold"), text_color=self.colors["accent"]).pack(pady=(15, 10), padx=15, anchor="w")

        self.opt_vars = {
            "clean_temp": ctk.BooleanVar(value=True),
            "clean_cache": ctk.BooleanVar(value=True),
            "optimize_ram": ctk.BooleanVar(value=True),
            "update_packages": ctk.BooleanVar(value=True),
            "check_integrity": ctk.BooleanVar(value=True),
            "disk_opt": ctk.BooleanVar(value=True),
            "scan_virus": ctk.BooleanVar(value=False)
        }
        
        opt_labels = [
            ("clean_temp", "[T] Limpar Temporários"),
            ("clean_cache", "[C] Limpar Cache"),
            ("optimize_ram", "[M] Otimizar RAM"),
            ("update_packages", "[U] Atualizar Pacotes"),
            ("check_integrity", "[I] Verificar Integridade"),
            ("disk_opt", "[D] Otimizar Disco"),
            ("scan_virus", "[V] Scan de Vírus")
        ]

        for key, text in opt_labels:
            sw = ctk.CTkSwitch(
                options_panel, text=text, variable=self.opt_vars[key],
                font=ctk.CTkFont(family="Courier", size=12),
                progress_color=self.colors["accent"], button_color="#ffffff",
                button_hover_color="#dddddd"
            )
            sw.pack(pady=10, padx=20, anchor="w")

        # Ações
        opt_actions = ctk.CTkFrame(options_panel, fg_color="transparent")
        opt_actions.pack(pady=20, padx=20, fill="x", side="bottom")

        self.start_btn = ctk.CTkButton(
            opt_actions, text=">> EXECUTAR", 
            font=ctk.CTkFont(family="Courier", size=14, weight="bold"),
            fg_color=self.colors["accent"], text_color="black", hover_color=self.colors["accent_hover"],
            command=self.start_optimization
        )
        self.start_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.stop_btn = ctk.CTkButton(
            opt_actions, text="[X] CANCELAR", 
            font=ctk.CTkFont(family="Courier", size=14, weight="bold"),
            fg_color="#ff0000", text_color="white", hover_color="#cc0000",
            state="disabled", command=self.stop_optimization
        )
        self.stop_btn.pack(side="right", expand=True, fill="x", padx=(5, 0))

        # Terminal Log
        log_panel = ctk.CTkFrame(self.frames["optimizer"], fg_color=self.colors["surface"], corner_radius=10)
        log_panel.grid(row=1, column=1, padx=(10, 20), pady=10, sticky="nsew")
        log_panel.grid_rowconfigure(0, weight=1)
        log_panel.grid_columnconfigure(0, weight=1)

        self.log_text = ProcessLogText(log_panel)
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        welcome_msg = "┌─────────────────────────────────────────────────┐\n" \
                      "│          PAGURO BOOST TERMINAL v2.0             │\n" \
                      "│                                                 │\n" \
                      "│  Sistema pronto para otimização...              │\n" \
                      "└─────────────────────────────────────────────────┘\n\n" \
                      "[SYSTEM] Terminal inicializado com sucesso.\n" \
                      "[READY] Aguardando comandos...\n\n"
        self.log_text.insert("end", welcome_msg)

        # Barra de Operação
        self.opt_progress = ctk.CTkProgressBar(self.frames["optimizer"], progress_color=self.colors["accent"])
        self.opt_progress.grid(row=2, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="ew")
        self.opt_progress.set(0)


        # --- FRAME 3: Análises ---
        self.frames["analysis"] = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frames["analysis"].grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            self.frames["analysis"], text=">>> CENTRAL DE ANÁLISES <<<",
            font=ctk.CTkFont(family="Courier", size=20, weight="bold"),
            text_color=self.colors["accent"]
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 30), sticky="nw")

        analyses = [
            ("Memória RAM", "Análise detalhada do uso de memória e top processos.", self.show_memory_analysis, 1, 0),
            ("Armazenamento", "Escaneamento de arquivos grandes, antigos e duplicatas.", self.show_disk_analysis, 1, 1),
            ("Performance", "Relatório avançado de estabilidade do sistema ao longo do tempo.", self.show_performance_report, 2, 0)
        ]

        for title, desc, cmd, row, col in analyses:
            card = ctk.CTkFrame(self.frames["analysis"], fg_color=self.colors["surface"], corner_radius=15)
            card.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")
            
            ctk.CTkLabel(card, text=f"[{title.upper()}]", font=ctk.CTkFont(family="Courier", size=16, weight="bold"), text_color=self.colors["accent"]).pack(pady=(20, 10), padx=20, anchor="w")
            ctk.CTkLabel(card, text=desc, font=ctk.CTkFont(family="Courier", size=12), text_color=self.colors["text_dim"], wraplength=300, justify="left").pack(pady=(0, 20), padx=20, anchor="w", fill="x", expand=True)
            
            ctk.CTkButton(
                card, text="INICIAR ANÁLISE >", 
                font=ctk.CTkFont(family="Courier", size=12, weight="bold"),
                fg_color="transparent", border_color=self.colors["accent"], border_width=1,
                text_color=self.colors["accent"], hover_color="#222222",
                command=cmd
            ).pack(pady=20, padx=20, fill="x")

    def select_frame_by_name(self, name):
        # Cor de destaque no menu lateral
        for btn_name, btn in self.nav_btns.items():
            if btn_name == name:
                btn.configure(fg_color=self.colors["surface"], text_color=self.colors["accent"])
            else:
                btn.configure(fg_color="transparent", text_color=self.colors["text"])
        
        # Ocultar todos os frames principais
        for frame in self.frames.values():
            frame.grid_forget()

        # Mostrar o selecionado
        self.frames[name].grid(row=0, column=1, sticky="nsew")

    # ---- MÉTODOS DE LÓGICA / BACKEND (Adaptados) ----

    def log_message(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_queue.put(f"[{timestamp}] {message}\n")

    def process_log_queue(self):
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.insert("end", message)
                self.log_text.see("end")
        except queue.Empty:
            pass
        self.after(100, self.process_log_queue)

    def refresh_system_info(self):
        def update_info():
            try:
                if not self.optimizer:
                    self.optimizer = SystemOptimizer()
                import platform
                is_wsl = 'microsoft' in platform.uname().release.lower()
                os_info = f"{platform.system()} {'(WSL)' if is_wsl else ''}"
                self.after(0, lambda: self.os_label.configure(text=f"SISTEMA:\n{os_info.upper()}"))
            except Exception as e:
                self.log_message(f"Erro ao atualizar info: {e}")
        threading.Thread(target=update_info, daemon=True).start()

    def get_color_for_percentage(self, percentage):
        if percentage >= 80: return self.colors["critical"]
        if percentage >= 60: return self.colors["warning"]
        return self.colors["accent"]

    def update_retro_display(self):
        try:
            if not self.optimizer:
                self.optimizer = SystemOptimizer()
            cpu, memory, disk = self.optimizer.medir_uso_recursos()

            # Update progress bars and labels
            self.progress_bars["cpu"].set(cpu / 100.0)
            self.progress_bars["cpu"].configure(progress_color=self.get_color_for_percentage(cpu))
            self.progress_labels["cpu"].configure(text=f"{cpu:5.1f}%")

            self.progress_bars["ram"].set(memory / 100.0)
            self.progress_bars["ram"].configure(progress_color=self.get_color_for_percentage(memory))
            self.progress_labels["ram"].configure(text=f"{memory:5.1f}%")

            self.progress_bars["hdd"].set(disk / 100.0)
            self.progress_bars["hdd"].configure(progress_color=self.get_color_for_percentage(disk))
            self.progress_labels["hdd"].configure(text=f"{disk:5.1f}%")

        except Exception as e:
            pass
        self.after(2000, self.update_retro_display)

    def start_optimization(self):
        if self.running: return
        self.running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.opt_progress.configure(mode="indeterminate")
        self.opt_progress.start()
        
        self.log_text.delete("1.0", "end")
        self.log_message("=== Iniciando Sequência de Otimização ===")
        threading.Thread(target=self.run_optimization, daemon=True).start()

    def run_optimization(self):
        try:
            if not self.optimizer: self.optimizer = SystemOptimizer()
            if not self.optimizer.verificar_gerenciador_pacotes():
                self.log_message("[!] Gerenciador de pacotes não disponível!")
                return
            
            self.log_message("[M] Medindo recursos iniciais...")
            cpu_init, mem_init, disk_init = self.optimizer.medir_uso_recursos()
            self.log_message(f"CPU: {cpu_init:.1f}% | RAM: {mem_init:.1f}% | HDD: {disk_init:.1f}%")

            operations = []
            if self.opt_vars["clean_temp"].get(): operations.append((self.optimizer.limpar_temporarios, "[T] Limpando arquivos temporários"))
            if self.opt_vars["clean_cache"].get(): operations.append((self.optimizer.limpar_cache_sistema, "[C] Limpando cache do sistema"))
            if self.opt_vars["optimize_ram"].get(): operations.append((self.optimizer.otimizar_memoria_ram, "[M] Otimizando memória RAM"))
            if self.opt_vars["update_packages"].get(): operations.append((self.optimizer.atualizar_pacotes, "[U] Atualizando pacotes"))
            if self.opt_vars["check_integrity"].get(): operations.append((self.optimizer.verificar_integridade, "[I] Verificando integridade"))
            if self.opt_vars["scan_virus"].get(): operations.append((self.optimizer.verificar_virus, "[V] Scan de vírus"))
            if self.opt_vars["disk_opt"].get(): operations.append((lambda: self.optimizer.otimizar_disco_avancado(limpar_antigos=True), "[D] Otimização avançada de disco"))

            for operation, desc in operations:
                if not self.running: break
                self.log_message(desc)
                try:
                    success = operation()
                    status = "[OK] Concluído" if success else "[!] Com avisos"
                    self.log_message(f"{desc} - {status}")
                except Exception as e:
                    self.log_message(f"{desc} - [ERR] Falha: {e}")

            if self.running:
                self.log_message("=== Relatório de Fechamento ===")
                cpu_end, mem_end, disk_end = self.optimizer.medir_uso_recursos()
                self.log_message(f"CPU: {cpu_init:.1f}% -> {cpu_end:.1f}%")
                self.log_message(f"RAM: {mem_init:.1f}% -> {mem_end:.1f}%")
                self.log_message(f"HDD: {disk_init:.1f}% -> {disk_end:.1f}%")
                self.log_message("[RECOMMEND] Reinicie o sistema para aplicar as otimizações profundas.")

        except Exception as e:
            self.log_message(f"[FATAL] Erro crasso na otimização: {e}")
        finally:
            self.after(0, self.finish_optimization)

    def stop_optimization(self):
        self.running = False
        self.log_message("[X] INTERRUPÇÃO DE OTIMIZAÇÃO SOLICITADA PELO USUÁRIO.")

    def finish_optimization(self):
        self.running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.opt_progress.stop()
        self.opt_progress.configure(mode="determinate")
        self.opt_progress.set(1.0)
        self.refresh_system_info()

    def toggle_monitoring(self):
        if not self.optimizer: self.optimizer = SystemOptimizer()
        if not self.monitoring:
            if self.optimizer.iniciar_monitoramento_continuo(30):
                self.monitoring = True
                self.monitor_btn.configure(text="[||] PAUSAR MONITOR LOG", text_color=self.colors["warning"], border_color=self.colors["warning"])
                self.log_message("[>] Monitoramento em segundo plano ATIVADO.")
            else:
                messagebox.showerror("Erro", "Falha ao acionar monitoramento.")
        else:
            self.optimizer.parar_monitoramento_continuo()
            self.monitoring = False
            self.monitor_btn.configure(text="[>] INICIAR MONITOR LOG", text_color=self.colors["text"], border_color=self.colors["accent"])
            self.log_message("[||] Monitoramento em segundo plano DESATIVADO.")

    def abstract_popup_window(self, title, size="700x550"):
        top = ctk.CTkToplevel(self)
        top.title(title)
        top.geometry(size)
        top.configure(fg_color=self.colors["bg"])
        top.transient(self)
        
        container = ctk.CTkScrollableFrame(top, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(container, text=f">>> {title.upper()} <<<", font=ctk.CTkFont(family="Courier", size=20, weight="bold"), text_color=self.colors["accent"]).pack(pady=(0, 20), anchor="w")
        
        return top, container

    def show_memory_analysis(self):
        def analyze():
            try:
                if not self.optimizer: self.optimizer = SystemOptimizer()
                analysis = self.optimizer.analisar_uso_memoria_detalhado()
                
                self.after(0, lambda: self._render_memory_analysis(analysis))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Erro", f"Erro crítico na análise: {e}"))
        threading.Thread(target=analyze, daemon=True).start()

    def _render_memory_analysis(self, analysis):
        top, container = self.abstract_popup_window("Análise de Memória RAM")
        
        # Info Box
        info = ctk.CTkFrame(container, fg_color=self.colors["surface"], corner_radius=10)
        info.pack(fill="x", pady=10)
        
        metrics = [
            f"Memória Total: {analysis.get('memoria_total_gb', 0)} GB",
            f"Memória Usada: {analysis.get('memoria_usada_gb', 0)} GB",
            f"Memória Livre: {analysis.get('memoria_livre_gb', 0)} GB",
            f"Uso Relativo : {analysis.get('percentual_uso', 0):.1f}%"
        ]
        
        for m in metrics:
            ctk.CTkLabel(info, text=m, font=ctk.CTkFont(family="Courier", size=14), text_color=self.colors["text"]).pack(anchor="w", padx=20, pady=5)
        
        # Processos Box
        proc = ctk.CTkFrame(container, fg_color=self.colors["surface"], corner_radius=10)
        proc.pack(fill="x", pady=20)
        ctk.CTkLabel(proc, text="[TOP 10 PROCESSOS EM MEMÓRIA]", font=ctk.CTkFont(family="Courier", size=14, weight="bold"), text_color=self.colors["accent"]).pack(anchor="w", padx=20, pady=10)
        
        for p in analysis.get('processos_top_memoria', []):
            line = f"{p['pid']:<8} | {p['memory_percent']:>5.1f}% | {p['memory_mb']:>7} MB | {p['name']}"
            ctk.CTkLabel(proc, text=line, font=ctk.CTkFont(family="Courier", size=12), text_color=self.colors["text"]).pack(anchor="w", padx=20, pady=2)
            
        # Recomendações
        recs = analysis.get('recomendacoes', [])
        if recs:
            rec_frame = ctk.CTkFrame(container, fg_color=self.colors["surface"], corner_radius=10)
            rec_frame.pack(fill="x", pady=10)
            ctk.CTkLabel(rec_frame, text="[RECOMENDAÇÕES DO SISTEMA]", font=ctk.CTkFont(family="Courier", size=14, weight="bold"), text_color=self.colors["warning"]).pack(anchor="w", padx=20, pady=10)
            for r in recs:
                ctk.CTkLabel(rec_frame, text=f"-> {r}", font=ctk.CTkFont(family="Courier", size=12), text_color=self.colors["text_dim"], wraplength=600, justify="left").pack(anchor="w", padx=20, pady=5)

    def show_disk_analysis(self):
        def analyze():
            try:
                if not self.optimizer: self.optimizer = SystemOptimizer()
                analysis = self.optimizer.analisar_uso_disco_detalhado()
                if analysis:
                    self.after(0, lambda: self._render_disk_analysis(analysis))
                else:
                    self.after(0, lambda: messagebox.showerror("Erro", "Erro ao acessar partições."))
            except Exception as e:
                pass
        threading.Thread(target=analyze, daemon=True).start()

    def _render_disk_analysis(self, analysis):
        top, container = self.abstract_popup_window("Análise de Armazenamento")
        
        info = ctk.CTkFrame(container, fg_color=self.colors["surface"], corner_radius=10)
        info.pack(fill="x", pady=10)
        
        ctk.CTkLabel(info, text=f"Diretório Raiz: {analysis.get('caminho', 'N/A')}", font=ctk.CTkFont(family="Courier", size=14, weight="bold")).pack(anchor="w", padx=20, pady=10)
        ctk.CTkLabel(info, text=f"Total: {analysis.get('espaco_total_gb', 0)} GB | Usado: {analysis.get('espaco_usado_gb', 0)} GB | Livre: {analysis.get('espaco_livre_gb', 0)} GB", font=ctk.CTkFont(family="Courier", size=12)).pack(anchor="w", padx=20, pady=5)
        
        # Dirs grandes
        dirs = analysis.get('diretorios_grandes', [])
        if dirs:
            df = ctk.CTkFrame(container, fg_color=self.colors["surface"], corner_radius=10)
            df.pack(fill="x", pady=10)
            ctk.CTkLabel(df, text="[DIRETÓRIOS CRÍTICOS (GRANDES)]", font=ctk.CTkFont(family="Courier", size=14, weight="bold"), text_color=self.colors["accent"]).pack(anchor="w", padx=20, pady=10)
            for d in dirs[:5]:
                nm = os.path.basename(d['caminho']) or d['caminho']
                ctk.CTkLabel(df, text=f"{nm} -> {d['tamanho_gb']:.1f} GB", font=ctk.CTkFont(family="Courier", size=12)).pack(anchor="w", padx=20, pady=2)

        # Arquivos antigos
        ant = analysis.get('arquivos_antigos', {})
        if ant and ant.get('total_arquivos', 0) > 0:
            af = ctk.CTkFrame(container, fg_color=self.colors["surface"], corner_radius=10)
            af.pack(fill="x", pady=10)
            ctk.CTkLabel(af, text=f"[ARQUIVOS ANTIGOS] Total: {ant['total_arquivos']} | Desperdício: {ant['tamanho_total_mb']:.1f} MB", font=ctk.CTkFont(family="Courier", size=14, weight="bold"), text_color=self.colors["warning"]).pack(anchor="w", padx=20, pady=10)
            for a in ant.get('sample_arquivos', [])[:5]:
                ctk.CTkLabel(af, text=f"{os.path.basename(a['arquivo'])} | {a['dias_antigo']} dias | {a['tamanho_mb']:.1f} MB", font=ctk.CTkFont(family="Courier", size=12), text_color=self.colors["text_dim"]).pack(anchor="w", padx=20, pady=2)

        recs = analysis.get('recomendacoes', [])
        if recs:
            rec_frame = ctk.CTkFrame(container, fg_color=self.colors["surface"], corner_radius=10)
            rec_frame.pack(fill="x", pady=10)
            ctk.CTkLabel(rec_frame, text="[SUGESTÕES DE LIMPEZA]", font=ctk.CTkFont(family="Courier", size=14, weight="bold"), text_color=self.colors["accent"]).pack(anchor="w", padx=20, pady=10)
            for r in recs:
                ctk.CTkLabel(rec_frame, text=f"-> {r}", font=ctk.CTkFont(family="Courier", size=12), wraplength=600, justify="left").pack(anchor="w", padx=20, pady=5)


    def show_performance_report(self):
        # Para simplificar na reescrita premium, vamos gerar direto 24h as default
        def generate():
            try:
                if not self.optimizer: self.optimizer = SystemOptimizer()
                report = self.optimizer.gerar_relatorio_performance(24)
                if 'error' in report:
                    self.after(0, lambda: messagebox.showwarning("Aviso", report['error']))
                    return
                self.after(0, lambda: self._render_performance_report(report))
            except Exception as e:
                pass
        threading.Thread(target=generate, daemon=True).start()

    def _render_performance_report(self, report):
        top, container = self.abstract_popup_window(f"Relatório de Estabilidade - {report.get('period', '24H')}")

        info = ctk.CTkFrame(container, fg_color=self.colors["surface"], corner_radius=10)
        info.pack(fill="x", pady=10)
        ctk.CTkLabel(info, text=f"Amostras: {report.get('sample_count', 0)} | Coleta: {report.get('generated_at', 'N/A')[:19]}", font=ctk.CTkFont(family="Courier", size=12)).pack(anchor="w", padx=20, pady=15)
        
        stab = report.get('stability', {})
        if stab:
            stf = ctk.CTkFrame(container, fg_color=self.colors["surface"], corner_radius=10)
            stf.pack(fill="x", pady=10)
            ctk.CTkLabel(stf, text=f"SCORE HORIZONTAL: {stab.get('stability_score', 'N/A')}", font=ctk.CTkFont(family="Courier", size=16, weight="bold"), text_color=self.colors["accent"]).pack(anchor="w", padx=20, pady=15)
            
        avg = report.get('averages', {}).get('averages', {})
        if avg:
            af = ctk.CTkFrame(container, fg_color=self.colors["surface"], corner_radius=10)
            af.pack(fill="x", pady=10)
            ctk.CTkLabel(af, text="[MÉDIAS REGISTRADAS]", font=ctk.CTkFont(family="Courier", size=14, weight="bold")).pack(anchor="w", padx=20, pady=10)
            ctk.CTkLabel(af, text=f"CPU: {avg.get('cpu_percent', 0):.1f}% | RAM: {avg.get('memory_percent', 0):.1f}% | HDD: {avg.get('disk_percent', 0):.1f}%", font=ctk.CTkFont(family="Courier", size=12)).pack(anchor="w", padx=20, pady=5)

        recs = report.get('recommendations', [])
        if recs:
            rf = ctk.CTkFrame(container, fg_color=self.colors["surface"], corner_radius=10)
            rf.pack(fill="x", pady=10)
            ctk.CTkLabel(rf, text="[CONCLUSÕES]", font=ctk.CTkFont(family="Courier", size=14, weight="bold"), text_color=self.colors["accent"]).pack(anchor="w", padx=20, pady=10)
            for r in recs:
                ctk.CTkLabel(rf, text=f"-> {r}", font=ctk.CTkFont(family="Courier", size=12), text_color=self.colors["text"], wraplength=600, justify="left").pack(anchor="w", padx=20, pady=5)

def main():
    app = PaguroBoostGUI()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()