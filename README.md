# Paguro Boost 🦀⚡

[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)](https://github.com/paguro-team/paguro-boost)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20WSL-lightgrey.svg)](https://github.com/paguro-team/paguro-boost)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A modern, cross-platform system optimizer with a retro GUI interface that provides advanced RAM optimization, disk cleanup, startup management, and performance monitoring.

## ✨ Features

### 🎮 Retro GUI Interface
- **80s/90s aesthetic** with green phosphorescent theme
- **Real-time monitoring** with ASCII progress bars
- **Terminal-style logs** with timestamps
- **Modern functionality** with vintage appearance

### 🧠 Advanced RAM Optimization
- **Process analysis** with memory usage breakdown
- **DNS cache clearing** for improved network performance
- **Working sets optimization** (Windows) and memory compaction (Linux)
- **Intelligent recommendations** based on system analysis

### 📊 Performance Monitoring
- **Historical metrics** stored in JSON format
- **Continuous monitoring** with configurable intervals
- **Stability scoring** and usage pattern analysis
- **Detailed performance reports** with trend analysis

### 🚀 Startup Optimization
- **Program classification** (Essential/Important/Optional/Unknown)
- **Boot time estimation** and measurement
- **Safe optimization** with user confirmation
- **Cross-platform startup analysis**

### 💽 Disk Optimization
- **Detailed space analysis** with directory size breakdown
- **Duplicate file detection** using MD5 hashing
- **Old file identification** with configurable age thresholds
- **Smart defragmentation** (Windows only, SSD-aware)

### 🛡️ Safety & Security
- **Administrator privileges** handled safely
- **Backup creation** before critical operations
- **Comprehensive logging** with rotation
- **Safe mode** for critical system areas

## Instalação

```bash
git clone https://github.com/seu-usuario/paguro-boost.git
cd paguro-boost
pip install -r requirements.txt
```

## Uso

### Interface Gráfica (Padrão)
```bash
python app.py
# ou explicitamente
python app.py --gui
```

### Linha de Comando (CLI)
```bash
python app.py --cli
```

### Apenas GUI
```bash
python gui.py
```

## Suporte

- ✅ **Windows**: winget, SFC, DISM, Microsoft Defender
- ✅ **Linux**: apt/yum/dnf/pacman, dpkg, ClamAV/rkhunter
- ✅ **WSL**: Detectado automaticamente

## Requisitos

- Python 3.6+
- psutil
- Permissões de administrador (opcional para algumas funções)

## Funcionalidades

### Windows
- Limpeza de arquivos temporários (%temp%, %windir%\Temp)
- Cache do Windows Update
- Verificação SFC e DISM
- Scan com Microsoft Defender
- Atualização via winget

### Linux
- Limpeza de /tmp, /var/tmp, ~/.cache
- Cache APT e logs do sistema
- Correção de pacotes quebrados
- Scan com ClamAV/rkhunter
- Atualização via gerenciador de pacotes

## Contribuição

Contribuições são bem-vindas! Abra uma issue ou envie um pull request.

## Licença

MIT