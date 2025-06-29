# Estrutura do Projeto Paguro Boost

Este documento descreve a arquitetura do projeto Paguro Boost v2.0, seguindo as melhores práticas de projetos Python profissionais.

## 📁 Estrutura de Diretórios

```
paguro-boost/
├── 📦 paguro_boost/          # Pacote principal do código fonte
│   ├── __init__.py           # Inicialização do pacote + versão
│   ├── __main__.py           # Entrada para execução como módulo
│   ├── app.py                # Classe principal SystemOptimizer
│   ├── gui.py                # Interface gráfica retro
│   ├── metrics.py            # Sistema de métricas e monitoramento
│   ├── config.py             # Configurações centralizadas
│   ├── logger.py             # Sistema de logging profissional
│   └── exceptions.py         # Hierarquia de exceções customizadas
│
├── 🧪 tests/                 # Testes unitários e funcionais
│   ├── __init__.py           # Inicialização dos testes
│   ├── test_paguro_boost.py  # Suite de testes principal (14 testes)
│   ├── teste_completo_final.py      # Demonstração completa das 5 etapas
│   └── teste_funcionalidades.py    # Testes funcionais específicos
│
├── 📜 scripts/               # Scripts auxiliares e utilitários
│   ├── __init__.py           # Inicialização dos scripts
│   └── run_tests.py          # Script para executar testes
│
├── 📊 logs/                  # Arquivos de log e métricas
│   ├── system_metrics.json   # Histórico de métricas do sistema
│   ├── system_optimizer.log  # Logs de otimização
│   └── windows_optimizer.log # Logs específicos do Windows
│
├── 📚 docs/                  # Documentação do projeto
│   └── PROJECT_STRUCTURE.md  # Este arquivo
│
├── 📋 README.md              # Documentação principal
├── 📝 CHANGELOG.md           # Histórico de mudanças
├── ⚙️ setup.py               # Configuração de instalação/distribuição
├── 📦 requirements.txt       # Dependências do projeto
└── 🔧 __init__.py           # Marcador de pacote raiz
```

## 🎯 Componentes Principais

### 🔧 Core System (`paguro_boost/`)
- **app.py**: Classe `SystemOptimizer` com todas as 5 etapas de otimização
- **gui.py**: Interface gráfica retro com tema phosphorescent
- **metrics.py**: Sistema de coleta e análise de métricas em tempo real
- **config.py**: Configurações JSON persistentes e customizáveis
- **logger.py**: Sistema de logging com rotação e níveis profissionais
- **exceptions.py**: Hierarquia de exceções para tratamento robusto de erros

### 🧪 Testing (`tests/`)
- **test_paguro_boost.py**: 14 testes unitários cobrindo toda funcionalidade
- **teste_completo_final.py**: Demonstração das 5 etapas implementadas
- **teste_funcionalidades.py**: Testes funcionais específicos

### 📜 Scripts (`scripts/`)
- **run_tests.py**: Execução automatizada dos testes

### 📊 Data (`logs/`)
- **system_metrics.json**: Histórico persistente de métricas do sistema
- ***.log**: Logs rotativos com diferentes níveis de verbosidade

## 🚀 Como Executar

### Como Módulo Python
```bash
python3 -m paguro_boost
```

### Executáveis Direct
```bash
# GUI (padrão)
paguro-boost

# CLI explícito
paguro-boost-cli

# GUI explícito
paguro-boost-gui
```

### Executar Testes
```bash
python3 -m tests.test_paguro_boost
# ou
python3 scripts/run_tests.py
```

## 🏗️ Arquitetura

### ✅ Seguindo Padrões Python
- ✅ **PEP 8**: Código formatado conforme padrões Python
- ✅ **Separação de responsabilidades**: Cada módulo tem função específica
- ✅ **Imports relativos**: Estrutura de pacote profissional
- ✅ **Type hints**: Anotações de tipo para melhor manutenção
- ✅ **Documentação**: Docstrings em todos os métodos
- ✅ **Logging profissional**: Sistema robusto de logs
- ✅ **Tratamento de exceções**: Hierarquia customizada
- ✅ **Testes abrangentes**: 14 testes unitários + funcionais
- ✅ **Configuração centralized**: JSON persistente
- ✅ **Entry points**: Executáveis via setuptools

### 🎯 Padrões de Qualidade
- **Modularidade**: Componentes independentes e reutilizáveis
- **Testabilidade**: Cobertura completa de testes
- **Manutenibilidade**: Código limpo e bem documentado
- **Extensibilidade**: Fácil adição de novas funcionalidades
- **Robustez**: Tratamento adequado de erros e edge cases
- **Performance**: Otimizações e monitoramento em tempo real

## 📦 Distribuição

O projeto está configurado para distribuição via:
- **pip install**: `setup.py` profissional
- **PyPI**: Pronto para upload
- **Executáveis**: Entry points configurados
- **Docker**: Estrutura compatível com containerização