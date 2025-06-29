# Paguro Boost 🦀⚡

Um otimizador de sistema cross-platform que funciona tanto no Windows quanto no Linux/WSL.

## Características

- 🔍 **Detecção automática** do sistema operacional
- 🧹 **Limpeza de arquivos temporários** e cache
- 📦 **Atualização automática** de pacotes (winget/apt/yum/dnf)
- 🔧 **Verificação de integridade** do sistema
- 🛡️ **Scan de vírus** opcional
- 📊 **Monitoramento de recursos** (CPU, memória, disco)

## Instalação

```bash
git clone https://github.com/seu-usuario/paguro-boost.git
cd paguro-boost
pip install -r requirements.txt
```

## Uso

```bash
python app.py
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