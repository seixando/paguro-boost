import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import Optional, Tuple, List, Dict
import psutil
import shutil
import platform
import time
import gc
from metrics import SystemMetrics

class SystemOptimizer:
    def __init__(self):
        self.is_windows = platform.system() == 'Windows'
        self.is_wsl = 'microsoft' in platform.uname().release.lower()
        
        log_file = 'system_optimizer.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Sistema detectado: {platform.system()} {'(WSL)' if self.is_wsl else ''}")
        
        # Inicializar sistema de métricas
        self.metrics = SystemMetrics()
        
        # Coletar métricas iniciais
        initial_metrics = self.metrics.collect_current_metrics()
        if initial_metrics:
            self.metrics.add_metrics_to_history(initial_metrics)
    
    def verificar_gerenciador_pacotes(self) -> bool:
        """Verifica se há um gerenciador de pacotes disponível."""
        if self.is_windows:
            return self._verificar_winget()
        else:
            return self._verificar_gerenciadores_linux()
    
    def _verificar_winget(self) -> bool:
        """Verifica se o winget está instalado no sistema."""
        try:
            if shutil.which("winget") is not None:
                self.logger.info("Winget está instalado.")
                return True
            else:
                self.logger.warning("Winget não está instalado.")
                self.logger.info("Para instalar o Winget, atualize o Windows ou baixe em:")
                self.logger.info("https://github.com/microsoft/winget-cli/releases")
                return False
        except Exception as e:
            self.logger.error(f"Erro ao verificar winget: {e}")
            return False
    
    def _verificar_gerenciadores_linux(self) -> bool:
        """Verifica gerenciadores de pacotes no Linux."""
        gerenciadores = ['apt', 'yum', 'dnf', 'pacman', 'zypper', 'snap', 'flatpak']
        encontrados = []
        
        for gerenciador in gerenciadores:
            if shutil.which(gerenciador):
                encontrados.append(gerenciador)
        
        if encontrados:
            self.logger.info(f"Gerenciadores encontrados: {', '.join(encontrados)}")
            return True
        else:
            self.logger.warning("Nenhum gerenciador de pacotes encontrado")
            return False

    def medir_uso_recursos(self) -> Tuple[float, float, float]:
        """Mede o uso de CPU, memória e disco."""
        try:
            uso_cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            uso_memoria = mem.percent
            
            # Usar C:\ em Windows ao invés de /
            disco = psutil.disk_usage('C:\\' if os.name == 'nt' else '/')
            uso_disco = disco.percent
            
            self.logger.info(f"CPU: {uso_cpu}% | Memória: {uso_memoria}% | Disco: {uso_disco}%")
            return uso_cpu, uso_memoria, uso_disco
        except Exception as e:
            self.logger.error(f"Erro ao medir recursos: {e}")
            return 0.0, 0.0, 0.0

    def _executar_comando(self, comando: str, descricao: str) -> bool:
        """Executa um comando do sistema com tratamento de erro."""
        try:
            result = subprocess.run(comando, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info(f"{descricao} - Sucesso")
                return True
            else:
                self.logger.warning(f"{descricao} - Aviso: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"{descricao} - Erro: {e}")
            return False
    
    def _executar_comando_sudo_opcional(self, comando: str, descricao: str) -> bool:
        """Executa comando com sudo, mas não falha se sudo não estiver disponível."""
        try:
            result = subprocess.run(comando, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info(f"{descricao} - Sucesso")
                return True
            elif "password is required" in result.stderr or "password required" in result.stderr:
                self.logger.info(f"{descricao} - Pulado (requer senha sudo)")
                return True  # Não considerar como falha
            else:
                self.logger.warning(f"{descricao} - Aviso: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"{descricao} - Erro: {e}")
            return False
    
    def limpar_temporarios(self) -> bool:
        """Limpa arquivos temporários do sistema."""
        if self.is_windows:
            return self._limpar_temporarios_windows()
        else:
            return self._limpar_temporarios_linux()
    
    def _limpar_temporarios_windows(self) -> bool:
        """Limpa arquivos temporários do Windows."""
        comandos = [
            ('del /q /s %temp%\\* 2>nul', 'Limpeza temp do usuário'),
            ('del /q /s %windir%\\Temp\\* 2>nul', 'Limpeza temp do Windows')
        ]
        
        sucesso = True
        for comando, desc in comandos:
            if not self._executar_comando(comando, desc):
                sucesso = False
        
        return sucesso
    
    def _limpar_temporarios_linux(self) -> bool:
        """Limpa arquivos temporários do Linux."""
        comandos = [
            ('sudo rm -rf /tmp/* 2>/dev/null', 'Limpeza /tmp'),
            ('sudo rm -rf /var/tmp/* 2>/dev/null', 'Limpeza /var/tmp'),
            ('rm -rf ~/.cache/* 2>/dev/null', 'Limpeza cache do usuário')
        ]
        
        sucesso = True
        for comando, desc in comandos:
            if not self._executar_comando(comando, desc):
                sucesso = False
        
        return sucesso

    def limpar_cache_sistema(self) -> bool:
        """Limpa o cache do sistema."""
        if self.is_windows:
            return self._limpar_cache_windows_update()
        else:
            return self._limpar_cache_linux()
    
    def _limpar_cache_windows_update(self) -> bool:
        """Limpa o cache do Windows Update."""
        comandos = [
            ('net stop wuauserv', 'Parando serviço Windows Update'),
            ('net stop bits', 'Parando serviço BITS'),
            ('del /f /s /q %windir%\\SoftwareDistribution\\Download 2>nul', 'Limpando cache'),
            ('net start wuauserv', 'Iniciando serviço Windows Update'),
            ('net start bits', 'Iniciando serviço BITS')
        ]
        
        sucesso = True
        for comando, desc in comandos:
            if not self._executar_comando(comando, desc):
                sucesso = False
        
        return sucesso
    
    def _limpar_cache_linux(self) -> bool:
        """Limpa caches do sistema Linux."""
        comandos = [
            ('sudo apt clean 2>/dev/null', 'Limpeza cache APT'),
            ('sudo apt autoremove -y 2>/dev/null', 'Remoção pacotes órfãos'),
            ('sudo journalctl --vacuum-time=7d 2>/dev/null', 'Limpeza logs do sistema')
        ]
        
        sucesso = True
        for comando, desc in comandos:
            if not self._executar_comando_sudo_opcional(comando, desc):
                sucesso = False
        
        return sucesso

    def verificar_virus(self) -> bool:
        """Executa verificação de vírus."""
        if self.is_windows:
            return self._verificar_virus_windows()
        else:
            return self._verificar_virus_linux()
    
    def _verificar_virus_windows(self) -> bool:
        """Verifica vírus no Windows com Microsoft Defender."""
        self.logger.info("Iniciando verificação de vírus com o Microsoft Defender...")
        
        defender_path = Path(r"C:\ProgramData\Microsoft\Windows Defender\Platform")
        
        try:
            if not defender_path.exists():
                self.logger.warning("Microsoft Defender não encontrado")
                return False
            
            versoes = [d for d in defender_path.iterdir() if d.is_dir()]
            if not versoes:
                self.logger.warning("Nenhuma versão do Defender encontrada")
                return False
            
            versao_mais_recente = sorted(versoes)[-1]
            mpcmdrun_path = versao_mais_recente / "MpCmdRun.exe"
            
            if mpcmdrun_path.exists():
                return self._executar_comando(
                    f'"{mpcmdrun_path}" -Scan -ScanType 2',
                    "Verificação de vírus"
                )
            else:
                self.logger.warning("MpCmdRun.exe não encontrado")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro na verificação de vírus: {e}")
            return False
    
    def _verificar_virus_linux(self) -> bool:
        """Verifica vírus no Linux usando ClamAV ou rkhunter."""
        if shutil.which('clamscan'):
            self.logger.info("Executando verificação com ClamAV...")
            return self._executar_comando(
                'clamscan -r --bell -i /home 2>/dev/null',
                'Verificação ClamAV'
            )
        elif shutil.which('rkhunter'):
            self.logger.info("Executando verificação com rkhunter...")
            return self._executar_comando_sudo_opcional(
                'sudo rkhunter --check --sk 2>/dev/null',
                'Verificação rkhunter'
            )
        else:
            self.logger.info("Nenhum antivírus encontrado (clamscan/rkhunter)")
            return True  # Não considerar como erro

    def atualizar_pacotes(self) -> bool:
        """Atualiza todos os pacotes do sistema."""
        if self.is_windows:
            return self._executar_comando(
                'winget upgrade --all --include-unknown',
                'Atualização de pacotes'
            )
        else:
            return self._atualizar_pacotes_linux()
    
    def _atualizar_pacotes_linux(self) -> bool:
        """Atualiza pacotes no Linux."""
        if shutil.which('apt'):
            return (self._executar_comando('sudo apt update', 'Atualizando lista de pacotes') and
                   self._executar_comando('sudo apt upgrade -y', 'Atualizando pacotes'))
        elif shutil.which('yum'):
            return self._executar_comando('sudo yum update -y', 'Atualizando pacotes')
        elif shutil.which('dnf'):
            return self._executar_comando('sudo dnf upgrade -y', 'Atualizando pacotes')
        elif shutil.which('pacman'):
            return self._executar_comando('sudo pacman -Syu --noconfirm', 'Atualizando pacotes')
        else:
            self.logger.warning("Nenhum gerenciador de pacotes suportado encontrado")
            return False
    
    def verificar_integridade(self) -> bool:
        """Executa verificação e correção de integridade do sistema."""
        if self.is_windows:
            return self._verificar_integridade_windows()
        else:
            return self._verificar_integridade_linux()
    
    def _verificar_integridade_windows(self) -> bool:
        """Verifica integridade do sistema Windows."""
        comandos = [
            ('sfc /scannow', 'Verificação SFC'),
            ('dism /online /cleanup-image /restorehealth', 'Correção DISM')
        ]
        
        sucesso = True
        for comando, desc in comandos:
            if not self._executar_comando(comando, desc):
                sucesso = False
        
        return sucesso
    
    def _verificar_integridade_linux(self) -> bool:
        """Verifica integridade do sistema Linux."""
        comandos = [
            ('sudo dpkg --configure -a 2>/dev/null', 'Configuração pacotes quebrados'),
            ('sudo apt --fix-broken install -y 2>/dev/null', 'Correção dependências')
        ]
        
        sucesso = True
        for comando, desc in comandos:
            if not self._executar_comando_sudo_opcional(comando, desc):
                sucesso = False
        
        return sucesso
    
    def otimizar_memoria_ram(self) -> bool:
        """Executa otimização avançada da memória RAM."""
        self.logger.info("Iniciando otimização avançada de RAM...")
        
        # Medição inicial
        mem_inicial = psutil.virtual_memory()
        self.logger.info(f"RAM inicial: {mem_inicial.percent:.1f}% ({mem_inicial.used // (1024**3):.1f}GB usada)")
        
        sucesso = True
        
        # 1. Garbage collection do Python
        gc.collect()
        
        # 2. Limpar cache de DNS
        sucesso &= self._limpar_cache_dns()
        
        # 3. Gerenciar processos com alto consumo
        sucesso &= self._gerenciar_processos_memoria()
        
        # 4. Otimizar serviços em background
        sucesso &= self._otimizar_servicos_background()
        
        # 5. Limpar working sets (Windows)
        if self.is_windows:
            sucesso &= self._limpar_working_sets_windows()
        else:
            sucesso &= self._otimizar_memoria_linux()
        
        # Medição final
        time.sleep(2)  # Aguardar efeito das otimizações
        mem_final = psutil.virtual_memory()
        liberada = (mem_inicial.used - mem_final.used) // (1024**2)  # MB
        
        self.logger.info(f"RAM final: {mem_final.percent:.1f}% ({mem_final.used // (1024**3):.1f}GB usada)")
        self.logger.info(f"Memória liberada: {liberada:.0f}MB")
        
        return sucesso
    
    def _limpar_cache_dns(self) -> bool:
        """Limpa o cache DNS para liberar memória."""
        if self.is_windows:
            return self._executar_comando(
                'ipconfig /flushdns',
                'Limpeza cache DNS'
            )
        else:
            # Linux - reiniciar systemd-resolved ou nscd
            comandos = [
                ('sudo systemctl restart systemd-resolved 2>/dev/null', 'Reiniciando systemd-resolved'),
                ('sudo systemctl restart nscd 2>/dev/null', 'Reiniciando nscd'),
                ('sudo service networking restart 2>/dev/null', 'Reiniciando networking')
            ]
            
            sucesso = False
            for comando, desc in comandos:
                if self._executar_comando_sudo_opcional(comando, desc):
                    sucesso = True
                    break
            
            return sucesso
    
    def _gerenciar_processos_memoria(self) -> bool:
        """Identifica e gerencia processos com alto consumo de memória."""
        try:
            processos_alto_consumo = []
            
            # Listar processos ordenados por uso de memória
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'memory_info']):
                try:
                    if proc.info['memory_percent'] > 5.0:  # Processos usando mais de 5% da RAM
                        processos_alto_consumo.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'memory_percent': proc.info['memory_percent'],
                            'memory_mb': proc.info['memory_info'].rss // (1024 * 1024)
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Ordenar por uso de memória
            processos_alto_consumo.sort(key=lambda x: x['memory_percent'], reverse=True)
            
            if processos_alto_consumo:
                self.logger.info("Processos com alto consumo de memória:")
                for proc in processos_alto_consumo[:5]:  # Top 5
                    self.logger.info(f"  {proc['name']}: {proc['memory_percent']:.1f}% ({proc['memory_mb']}MB)")
                
                # Otimizar processos específicos conhecidos
                self._otimizar_processos_conhecidos(processos_alto_consumo)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao gerenciar processos: {e}")
            return False
    
    def _otimizar_processos_conhecidos(self, processos: List[Dict]) -> bool:
        """Otimiza processos conhecidos que podem ser otimizados."""
        processos_navegadores = ['chrome.exe', 'firefox.exe', 'msedge.exe', 'opera.exe']
        processos_otimizar = []
        
        for proc in processos:
            nome_lower = proc['name'].lower()
            if any(navegador in nome_lower for navegador in processos_navegadores):
                processos_otimizar.append(proc)
        
        if processos_otimizar:
            self.logger.info("Sugestão: Feche abas desnecessárias do navegador para liberar mais memória")
        
        return True
    
    def _otimizar_servicos_background(self) -> bool:
        """Otimiza serviços em background desnecessários."""
        if self.is_windows:
            # Serviços Windows que podem ser parados temporariamente
            servicos_otimizar = [
                'SysMain',  # Superfetch
                'Themes',   # Temas (se não precisar)
                'WSearch'   # Windows Search (temporariamente)
            ]
            
            sucesso = True
            for servico in servicos_otimizar:
                comando = f'sc query "{servico}" >nul 2>&1 && net stop "{servico}" 2>nul'
                if self._executar_comando(comando, f'Parando serviço {servico}'):
                    self.logger.info(f"Serviço {servico} parado temporariamente")
                
            return sucesso
        else:
            # Linux - não parar serviços críticos, apenas sugerir
            self.logger.info("Linux: Serviços em background mantidos por segurança")
            return True
    
    def _limpar_working_sets_windows(self) -> bool:
        """Força limpeza de working sets no Windows."""
        try:
            # Usar comando empty.exe se disponível, senão usar powershell
            comando_powershell = '''
            [System.GC]::Collect()
            [System.GC]::WaitForPendingFinalizers()
            [System.GC]::Collect()
            '''
            
            return self._executar_comando(
                f'powershell -Command "{comando_powershell}"',
                'Limpeza working sets'
            )
        except Exception as e:
            self.logger.error(f"Erro na limpeza de working sets: {e}")
            return False
    
    def _otimizar_memoria_linux(self) -> bool:
        """Otimizações específicas de memória para Linux."""
        comandos = [
            # Limpar page cache, dentries e inodes
            ('echo 1 | sudo tee /proc/sys/vm/drop_caches 2>/dev/null', 'Limpeza page cache'),
            ('echo 2 | sudo tee /proc/sys/vm/drop_caches 2>/dev/null', 'Limpeza dentries/inodes'),
            ('echo 3 | sudo tee /proc/sys/vm/drop_caches 2>/dev/null', 'Limpeza cache completa'),
            # Compactar memória
            ('echo 1 | sudo tee /proc/sys/vm/compact_memory 2>/dev/null', 'Compactação de memória')
        ]
        
        sucesso = True
        for comando, desc in comandos:
            if not self._executar_comando_sudo_opcional(comando, desc):
                sucesso = False
        
        return sucesso
    
    def analisar_uso_memoria_detalhado(self) -> Dict:
        """Fornece análise detalhada do uso de memória."""
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Análise por processo
            processos_memoria = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'memory_info']):
                try:
                    if proc.info['memory_percent'] > 1.0:  # Mais de 1% da RAM
                        processos_memoria.append({
                            'name': proc.info['name'],
                            'pid': proc.info['pid'],
                            'memory_percent': proc.info['memory_percent'],
                            'memory_mb': proc.info['memory_info'].rss // (1024 * 1024)
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            processos_memoria.sort(key=lambda x: x['memory_percent'], reverse=True)
            
            analise = {
                'memoria_total_gb': mem.total // (1024**3),
                'memoria_usada_gb': mem.used // (1024**3),
                'memoria_livre_gb': mem.available // (1024**3),
                'percentual_uso': mem.percent,
                'swap_total_gb': swap.total // (1024**3) if swap.total > 0 else 0,
                'swap_usado_gb': swap.used // (1024**3) if swap.used > 0 else 0,
                'processos_top_memoria': processos_memoria[:10],
                'recomendacoes': self._gerar_recomendacoes_memoria(mem, processos_memoria)
            }
            
            return analise
            
        except Exception as e:
            self.logger.error(f"Erro na análise de memória: {e}")
            return {}
    
    def _gerar_recomendacoes_memoria(self, mem, processos) -> List[str]:
        """Gera recomendações baseadas no uso de memória."""
        recomendacoes = []
        
        if mem.percent > 85:
            recomendacoes.append("⚠️ Uso crítico de memória (>85%). Execute otimização urgente.")
        elif mem.percent > 70:
            recomendacoes.append("⚠️ Uso alto de memória (>70%). Considere otimização.")
        
        # Analisar processos
        navegadores = sum(1 for p in processos if any(nav in p['name'].lower() 
                         for nav in ['chrome', 'firefox', 'edge', 'opera']))
        if navegadores > 3:
            recomendacoes.append(f"🌐 {navegadores} processos de navegador ativos. Feche abas desnecessárias.")
        
        # Verificar swap
        swap = psutil.swap_memory()
        if swap.used > 0:
            recomendacoes.append(f"💾 Usando {swap.used//(1024**2)}MB de swap. Adicione mais RAM se possível.")
        
        return recomendacoes
    
    def iniciar_monitoramento_continuo(self, interval: int = 30) -> bool:
        """Inicia monitoramento contínuo de métricas."""
        self.logger.info(f"Iniciando monitoramento contínuo (intervalo: {interval}s)")
        return self.metrics.start_monitoring(interval)
    
    def parar_monitoramento_continuo(self):
        """Para o monitoramento contínuo."""
        self.logger.info("Parando monitoramento contínuo")
        self.metrics.stop_monitoring()
    
    def gerar_relatorio_performance(self, horas: int = 24) -> Dict:
        """Gera relatório detalhado de performance."""
        self.logger.info(f"Gerando relatório de performance ({horas}h)")
        return self.metrics.generate_performance_report(horas)
    
    def obter_metricas_periodo(self, horas: int = 24) -> List[Dict]:
        """Obtém métricas de um período específico."""
        return self.metrics.get_metrics_in_range(horas)
    
    def calcular_medias_periodo(self, horas: int = 24) -> Dict:
        """Calcula médias das métricas em um período."""
        return self.metrics.calculate_averages(horas)
    
    def limpar_historico_antigo(self, dias: int = 7) -> int:
        """Remove dados antigos do histórico de métricas."""
        registros_restantes = self.metrics.cleanup_old_data(dias)
        self.logger.info(f"Limpeza do histórico concluída. {registros_restantes} registros mantidos.")
        return registros_restantes
    
    def coletar_metricas_detalhadas(self) -> Dict:
        """Coleta métricas detalhadas do momento atual."""
        metricas = self.metrics.collect_current_metrics()
        if metricas:
            self.metrics.add_metrics_to_history(metricas)
        return metricas
    
    def analisar_programas_inicializacao(self) -> Dict:
        """Analisa programas de inicialização do sistema."""
        try:
            if self.is_windows:
                return self._analisar_startup_windows()
            else:
                return self._analisar_startup_linux()
        except Exception as e:
            self.logger.error(f"Erro ao analisar programas de inicialização: {e}")
            return {}
    
    def _analisar_startup_windows(self) -> Dict:
        """Analisa programas de startup no Windows."""
        startup_programs = []
        
        try:
            # Usar wmic para obter programas de startup
            import subprocess
            result = subprocess.run(
                'wmic startup get name,command,location /format:csv',
                shell=True, capture_output=True, text=True, encoding='utf-8'
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Pular header
                for line in lines:
                    if line.strip():
                        parts = line.split(',')
                        if len(parts) >= 4:
                            startup_programs.append({
                                'name': parts[2].strip() if len(parts) > 2 else 'Desconhecido',
                                'command': parts[1].strip() if len(parts) > 1 else '',
                                'location': parts[3].strip() if len(parts) > 3 else ''
                            })
            
            # Também verificar registro do Windows
            startup_programs.extend(self._verificar_registro_startup())
            
        except Exception as e:
            self.logger.error(f"Erro ao obter programas de startup: {e}")
        
        # Classificar programas
        classificacao = self._classificar_programas_startup(startup_programs)
        
        return {
            'programas': startup_programs,
            'total': len(startup_programs),
            'classificacao': classificacao,
            'tempo_boot_estimado': self._estimar_tempo_boot(len(startup_programs)),
            'recomendacoes': self._gerar_recomendacoes_startup(classificacao)
        }
    
    def _verificar_registro_startup(self) -> List[Dict]:
        """Verifica registro do Windows para programas de startup."""
        startup_programs = []
        
        try:
            import winreg
            
            # Chaves do registro para verificar
            chaves = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce")
            ]
            
            for hive, chave_path in chaves:
                try:
                    with winreg.OpenKey(hive, chave_path) as chave:
                        i = 0
                        while True:
                            try:
                                nome, comando, _ = winreg.EnumValue(chave, i)
                                startup_programs.append({
                                    'name': nome,
                                    'command': comando,
                                    'location': f"Registry: {chave_path}"
                                })
                                i += 1
                            except WindowsError:
                                break
                except WindowsError:
                    continue
                    
        except ImportError:
            # winreg não disponível (não Windows)
            pass
        except Exception as e:
            self.logger.error(f"Erro ao verificar registro: {e}")
        
        return startup_programs
    
    def _analisar_startup_linux(self) -> Dict:
        """Analisa programas de startup no Linux."""
        startup_programs = []
        
        try:
            # Verificar diretórios de autostart
            autostart_dirs = [
                os.path.expanduser("~/.config/autostart"),
                "/etc/xdg/autostart",
                "/usr/share/applications"
            ]
            
            for autostart_dir in autostart_dirs:
                if os.path.exists(autostart_dir):
                    for filename in os.listdir(autostart_dir):
                        if filename.endswith('.desktop'):
                            desktop_file = os.path.join(autostart_dir, filename)
                            program_info = self._parse_desktop_file(desktop_file)
                            if program_info:
                                startup_programs.append(program_info)
            
            # Verificar serviços systemd do usuário
            startup_programs.extend(self._verificar_systemd_user_services())
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar startup Linux: {e}")
        
        classificacao = self._classificar_programas_startup(startup_programs)
        
        return {
            'programas': startup_programs,
            'total': len(startup_programs),
            'classificacao': classificacao,
            'tempo_boot_estimado': self._estimar_tempo_boot(len(startup_programs)),
            'recomendacoes': self._gerar_recomendacoes_startup(classificacao)
        }
    
    def _parse_desktop_file(self, filepath: str) -> Optional[Dict]:
        """Faz parse de arquivo .desktop do Linux."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            name = "Desconhecido"
            exec_cmd = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith("Name="):
                    name = line.split("=", 1)[1]
                elif line.startswith("Exec="):
                    exec_cmd = line.split("=", 1)[1]
            
            return {
                'name': name,
                'command': exec_cmd,
                'location': filepath
            }
            
        except Exception:
            return None
    
    def _verificar_systemd_user_services(self) -> List[Dict]:
        """Verifica serviços systemd do usuário."""
        services = []
        
        try:
            result = subprocess.run(
                'systemctl --user list-unit-files --type=service --state=enabled',
                shell=True, capture_output=True, text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')[1:]  # Pular header
                for line in lines:
                    if line.strip() and 'enabled' in line:
                        service_name = line.split()[0]
                        services.append({
                            'name': service_name,
                            'command': f'systemctl --user start {service_name}',
                            'location': 'systemd user service'
                        })
        except Exception:
            pass
        
        return services
    
    def _classificar_programas_startup(self, programas: List[Dict]) -> Dict:
        """Classifica programas de startup por importância."""
        essenciais = []
        importantes = []
        opcionais = []
        desconhecidos = []
        
        # Listas de programas conhecidos
        programas_essenciais = [
            'windows security', 'antivirus', 'windows defender', 'audio driver',
            'display driver', 'network manager', 'bluetooth', 'wifi'
        ]
        
        programas_importantes = [
            'nvidia', 'amd', 'intel', 'realtek', 'steam', 'discord',
            'skype', 'zoom', 'office', 'adobe'
        ]
        
        programas_opcionais = [
            'spotify', 'chrome', 'firefox', 'update', 'acrobat reader',
            'winrar', '7zip', 'dropbox', 'onedrive', 'google drive'
        ]
        
        for programa in programas:
            nome_lower = programa.get('name', '').lower()
            comando_lower = programa.get('command', '').lower()
            
            # Verificar se é essencial
            if any(ess in nome_lower or ess in comando_lower for ess in programas_essenciais):
                essenciais.append(programa)
            # Verificar se é importante
            elif any(imp in nome_lower or imp in comando_lower for imp in programas_importantes):
                importantes.append(programa)
            # Verificar se é opcional
            elif any(opt in nome_lower or opt in comando_lower for opt in programas_opcionais):
                opcionais.append(programa)
            else:
                desconhecidos.append(programa)
        
        return {
            'essenciais': essenciais,
            'importantes': importantes,
            'opcionais': opcionais,
            'desconhecidos': desconhecidos
        }
    
    def _estimar_tempo_boot(self, num_programas: int) -> str:
        """Estima tempo de boot baseado no número de programas."""
        if num_programas <= 5:
            return "Rápido (< 30s)"
        elif num_programas <= 10:
            return "Normal (30-60s)"
        elif num_programas <= 20:
            return "Lento (1-2 min)"
        else:
            return "Muito Lento (> 2 min)"
    
    def _gerar_recomendacoes_startup(self, classificacao: Dict) -> List[str]:
        """Gera recomendações para otimização de startup."""
        recomendacoes = []
        
        num_opcionais = len(classificacao.get('opcionais', []))
        num_desconhecidos = len(classificacao.get('desconhecidos', []))
        
        if num_opcionais > 5:
            recomendacoes.append(f"⚠️ {num_opcionais} programas opcionais no startup. Considere desabilitar alguns.")
        
        if num_desconhecidos > 3:
            recomendacoes.append(f"❓ {num_desconhecidos} programas desconhecidos. Investigue se são necessários.")
        
        total_nao_essenciais = num_opcionais + num_desconhecidos
        if total_nao_essenciais > 8:
            recomendacoes.append("🚀 Desabilitar programas desnecessários pode acelerar boot em 50-70%.")
        
        if not recomendacoes:
            recomendacoes.append("✅ Configuração de startup otimizada!")
        
        return recomendacoes
    
    def otimizar_inicializacao(self, desabilitar_opcionais: bool = False, 
                              desabilitar_desconhecidos: bool = False) -> bool:
        """Otimiza programas de inicialização."""
        self.logger.info("Iniciando otimização de inicialização...")
        
        try:
            analise = self.analisar_programas_inicializacao()
            
            if not analise.get('programas'):
                self.logger.warning("Nenhum programa de startup encontrado para otimizar")
                return False
            
            programas_desabilitar = []
            
            if desabilitar_opcionais:
                programas_desabilitar.extend(analise['classificacao'].get('opcionais', []))
            
            if desabilitar_desconhecidos:
                programas_desabilitar.extend(analise['classificacao'].get('desconhecidos', []))
            
            if not programas_desabilitar:
                self.logger.info("Nenhum programa selecionado para desabilitar")
                return True
            
            sucesso = True
            for programa in programas_desabilitar:
                if self._desabilitar_programa_startup(programa):
                    self.logger.info(f"Desabilitado: {programa.get('name', 'Desconhecido')}")
                else:
                    self.logger.warning(f"Falha ao desabilitar: {programa.get('name', 'Desconhecido')}")
                    sucesso = False
            
            self.logger.info(f"Otimização concluída. {len(programas_desabilitar)} programas processados.")
            return sucesso
            
        except Exception as e:
            self.logger.error(f"Erro na otimização de inicialização: {e}")
            return False
    
    def _desabilitar_programa_startup(self, programa: Dict) -> bool:
        """Desabilita um programa específico do startup."""
        try:
            if self.is_windows:
                return self._desabilitar_startup_windows(programa)
            else:
                return self._desabilitar_startup_linux(programa)
        except Exception as e:
            self.logger.error(f"Erro ao desabilitar programa: {e}")
            return False
    
    def _desabilitar_startup_windows(self, programa: Dict) -> bool:
        """Desabilita programa de startup no Windows."""
        nome = programa.get('name', '')
        
        # Usar PowerShell para desabilitar via Task Manager
        comando = f'''
        $app = Get-CimInstance -ClassName Win32_StartupCommand | Where-Object {{$_.Name -like "*{nome}*"}}
        if ($app) {{
            Disable-ScheduledTask -TaskName $app.Name -ErrorAction SilentlyContinue
        }}
        '''
        
        return self._executar_comando(
            f'powershell -Command "{comando}"',
            f'Desabilitando {nome}'
        )
    
    def _desabilitar_startup_linux(self, programa: Dict) -> bool:
        """Desabilita programa de startup no Linux."""
        location = programa.get('location', '')
        
        if '.desktop' in location and os.path.exists(location):
            # Mover arquivo .desktop para backup
            backup_dir = os.path.expanduser("~/.config/autostart_disabled")
            os.makedirs(backup_dir, exist_ok=True)
            
            backup_path = os.path.join(backup_dir, os.path.basename(location))
            
            try:
                shutil.move(location, backup_path)
                return True
            except Exception:
                return False
        
        elif 'systemd' in location:
            nome = programa.get('name', '')
            return self._executar_comando(
                f'systemctl --user disable {nome}',
                f'Desabilitando serviço {nome}'
            )
        
        return False
    
    def medir_tempo_boot(self) -> Dict:
        """Mede tempo de boot do sistema."""
        try:
            boot_time = psutil.boot_time()
            tempo_desde_boot = time.time() - boot_time
            
            # No Windows, tentar obter tempo de boot mais preciso
            if self.is_windows:
                try:
                    result = subprocess.run(
                        'wmic os get LastBootUpTime /format:csv',
                        shell=True, capture_output=True, text=True
                    )
                    # Processar resultado se necessário
                except:
                    pass
            
            return {
                'boot_timestamp': boot_time,
                'tempo_desde_boot_segundos': tempo_desde_boot,
                'tempo_desde_boot_formatado': self._formatar_tempo(tempo_desde_boot),
                'boot_datetime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(boot_time))
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao medir tempo de boot: {e}")
            return {}
    
    def _formatar_tempo(self, segundos: float) -> str:
        """Formata tempo em segundos para formato legível."""
        horas = int(segundos // 3600)
        minutos = int((segundos % 3600) // 60)
        segundos_rest = int(segundos % 60)
        
        if horas > 0:
            return f"{horas}h {minutos}m {segundos_rest}s"
        elif minutos > 0:
            return f"{minutos}m {segundos_rest}s"
        else:
            return f"{segundos_rest}s"
    
    def limpar_prefetch(self) -> bool:
        """Limpa arquivos prefetch (Windows) ou equivalentes (Linux)."""
        if self.is_windows:
            return self._executar_comando(
                'del /q /s %windir%\\Prefetch\\* 2>nul',
                'Limpeza do Prefetch'
            )
        else:
            # No Linux, limpar thumbnails e cache de ícones
            return self._executar_comando(
                'rm -rf ~/.thumbnails/* ~/.cache/thumbnails/* 2>/dev/null',
                'Limpeza thumbnails e cache de ícones'
            )
    
    def executar_otimizacao_completa(self) -> None:
        """Executa todas as rotinas de otimização."""
        if not self.verificar_gerenciador_pacotes():
            self.logger.error("Gerenciador de pacotes não disponível. Abortando otimização.")
            return
        
        self.logger.info("=== Iniciando otimização do sistema ===")
        
        # Medições iniciais
        self.logger.info("Medições antes da limpeza:")
        cpu_inicial, mem_inicial, disco_inicial = self.medir_uso_recursos()
        
        # Executar limpezas
        self.logger.info("Executando rotinas de limpeza e otimização:")
        operacoes = [
            (self.limpar_temporarios, "Limpeza de temporários"),
            (self.limpar_cache_sistema, "Limpeza cache do sistema"),
            (self.otimizar_memoria_ram, "Otimização avançada de RAM"),
            (self.atualizar_pacotes, "Atualização de pacotes"),
            (self.verificar_integridade, "Verificação de integridade"),
            (self.limpar_prefetch, "Limpeza de cache adicional"),
            (self.verificar_virus, "Verificação de vírus")
        ]
        
        for operacao, nome in operacoes:
            try:
                operacao()
            except Exception as e:
                self.logger.error(f"Erro em {nome}: {e}")
        
        # Medições finais
        self.logger.info("Medições após a limpeza:")
        cpu_final, mem_final, disco_final = self.medir_uso_recursos()
        
        # Relatório final
        self.logger.info("=== Relatório de Otimização ===")
        self.logger.info(f"Variação CPU: {cpu_inicial - cpu_final:.2f}%")
        self.logger.info(f"Variação Memória: {mem_inicial - mem_final:.2f}%")
        self.logger.info(f"Variação Disco: {disco_inicial - disco_final:.2f}%")
        self.logger.info("Recomendação: Reinicie o sistema para melhor desempenho.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Paguro Boost - Otimizador de Sistema')
    parser.add_argument('--cli', action='store_true', help='Executar em modo CLI (linha de comando)')
    parser.add_argument('--gui', action='store_true', help='Executar em modo GUI (interface gráfica)')
    args = parser.parse_args()
    
    # Se nenhum argumento for especificado, usar GUI por padrão
    if not args.cli and not args.gui:
        args.gui = True
    
    if args.gui:
        try:
            from gui import main as gui_main
            gui_main()
        except ImportError:
            print("Erro: tkinter não está disponível. Executando em modo CLI...")
            args.cli = True
        except Exception as e:
            print(f"Erro ao iniciar GUI: {e}")
            print("Executando em modo CLI...")
            args.cli = True
    
    if args.cli:
        try:
            optimizer = SystemOptimizer()
            optimizer.executar_otimizacao_completa()
        except KeyboardInterrupt:
            print("\nOperação cancelada pelo usuário.")
            sys.exit(1)
        except Exception as e:
            print(f"Erro fatal: {e}")
            sys.exit(1)
