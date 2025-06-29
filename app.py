import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import psutil
import shutil
import platform

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
    try:
        optimizer = SystemOptimizer()
        optimizer.executar_otimizacao_completa()
    except KeyboardInterrupt:
        print("\nOperação cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"Erro fatal: {e}")
        sys.exit(1)
