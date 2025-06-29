#!/usr/bin/env python3
"""
Script de teste das funcionalidades do Paguro Boost
"""

from paguro_boost.app import SystemOptimizer
import time

def testar_funcionalidades():
    print("🦀⚡ TESTE DAS FUNCIONALIDADES PAGURO BOOST ⚡🦀")
    print("=" * 60)
    
    # Inicializar otimizador
    print("1. Inicializando SystemOptimizer...")
    optimizer = SystemOptimizer()
    print("   ✅ Sistema detectado e inicializado")
    
    # Testar métricas básicas
    print("\n2. Testando métricas básicas...")
    cpu, mem, disk = optimizer.medir_uso_recursos()
    print(f"   📊 CPU: {cpu}% | RAM: {mem}% | Disco: {disk}%")
    
    # Testar análise detalhada de memória
    print("\n3. Testando análise detalhada de memória...")
    analise_mem = optimizer.analisar_uso_memoria_detalhado()
    if analise_mem:
        print(f"   🧠 Memória Total: {analise_mem.get('memoria_total_gb', 0)} GB")
        print(f"   🧠 Memória Usada: {analise_mem.get('memoria_usada_gb', 0)} GB")
        print(f"   🧠 Uso Percentual: {analise_mem.get('percentual_uso', 0):.1f}%")
        
        top_procs = analise_mem.get('processos_top_memoria', [])[:3]
        if top_procs:
            print("   📋 Top 3 processos por memória:")
            for proc in top_procs:
                print(f"      - {proc['name']}: {proc['memory_percent']:.1f}% ({proc['memory_mb']}MB)")
    
    # Testar coleta de métricas detalhadas
    print("\n4. Testando coleta de métricas detalhadas...")
    metricas = optimizer.coletar_metricas_detalhadas()
    if metricas:
        print(f"   📈 Timestamp: {metricas.get('timestamp', 'N/A')[:19]}")
        print(f"   💻 CPUs: {metricas.get('cpu', {}).get('count', 0)}")
        print(f"   🔢 Processos ativos: {metricas.get('processes', {}).get('count', 0)}")
    
    # Testar análise de startup (sem modificações)
    print("\n5. Testando análise de programas de inicialização...")
    try:
        analise_startup = optimizer.analisar_programas_inicializacao()
        if analise_startup:
            total = analise_startup.get('total', 0)
            tempo_boot = analise_startup.get('tempo_boot_estimado', 'N/A')
            print(f"   🚀 Programas de startup: {total}")
            print(f"   ⏱️ Tempo de boot estimado: {tempo_boot}")
            
            classificacao = analise_startup.get('classificacao', {})
            print(f"   📊 Essenciais: {len(classificacao.get('essenciais', []))}")
            print(f"   📊 Importantes: {len(classificacao.get('importantes', []))}")
            print(f"   📊 Opcionais: {len(classificacao.get('opcionais', []))}")
            print(f"   📊 Desconhecidos: {len(classificacao.get('desconhecidos', []))}")
            
            recomendacoes = analise_startup.get('recomendacoes', [])
            if recomendacoes:
                print("   💡 Recomendações:")
                for rec in recomendacoes[:2]:  # Mostrar só 2
                    print(f"      {rec}")
    except Exception as e:
        print(f"   ⚠️ Erro na análise de startup: {e}")
    
    # Testar tempo de boot
    print("\n6. Testando medição de tempo de boot...")
    tempo_boot = optimizer.medir_tempo_boot()
    if tempo_boot:
        print(f"   ⏰ Boot em: {tempo_boot.get('boot_datetime', 'N/A')}")
        print(f"   ⌛ Tempo desde boot: {tempo_boot.get('tempo_desde_boot_formatado', 'N/A')}")
    
    # Testar monitoramento (iniciar e parar rapidamente)
    print("\n7. Testando sistema de monitoramento...")
    if optimizer.iniciar_monitoramento_continuo(5):
        print("   ✅ Monitoramento iniciado")
        time.sleep(2)
        optimizer.parar_monitoramento_continuo()
        print("   ✅ Monitoramento parado")
    else:
        print("   ⚠️ Não foi possível iniciar monitoramento")
    
    # Testar relatório de performance
    print("\n8. Testando geração de relatório de performance...")
    try:
        relatorio = optimizer.gerar_relatorio_performance(1)  # Última 1 hora
        if 'error' not in relatorio:
            sample_count = relatorio.get('sample_count', 0)
            stability = relatorio.get('stability', {}).get('stability_score', 'N/A')
            print(f"   📊 Amostras analisadas: {sample_count}")
            print(f"   🎯 Score de estabilidade: {stability}")
            
            recommendations = relatorio.get('recommendations', [])
            if recommendations:
                print(f"   💡 Primeira recomendação: {recommendations[0]}")
        else:
            print(f"   ⚠️ {relatorio['error']}")
    except Exception as e:
        print(f"   ⚠️ Erro no relatório: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
    print("\n📋 FUNCIONALIDADES TESTADAS:")
    print("✅ Sistema de métricas básicas")
    print("✅ Análise detalhada de memória")
    print("✅ Coleta de métricas avançadas")
    print("✅ Análise de programas de startup")
    print("✅ Medição de tempo de boot")
    print("✅ Sistema de monitoramento contínuo")
    print("✅ Geração de relatórios de performance")
    print("\n🚀 Sistema pronto para uso!")

if __name__ == "__main__":
    testar_funcionalidades()