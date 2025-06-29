import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import psutil
import threading


class SystemMetrics:
    def __init__(self, history_file: str = "system_metrics.json"):
        self.history_file = history_file
        self.monitoring = False
        self.monitor_thread = None
        self.monitor_interval = 30  # segundos
        self.history_data = self._load_history()
        
    def _load_history(self) -> List[Dict]:
        """Carrega histórico de métricas do arquivo."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def _save_history(self):
        """Salva histórico de métricas no arquivo."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history_data, f, indent=2)
        except IOError as e:
            print(f"Erro ao salvar histórico: {e}")
    
    def collect_current_metrics(self) -> Dict:
        """Coleta métricas atuais do sistema."""
        try:
            # Métricas básicas
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('C:\\' if os.name == 'nt' else '/')
            
            # Métricas de rede
            net_io = psutil.net_io_counters()
            
            # Métricas de temperatura (se disponível)
            temperatures = self._get_temperatures()
            
            # Contadores de processos
            process_count = len(psutil.pids())
            
            # Top processos por CPU e memória
            top_cpu_processes = self._get_top_processes_cpu()
            top_memory_processes = self._get_top_processes_memory()
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count(),
                    'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percent': memory.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                },
                'network': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                },
                'processes': {
                    'count': process_count,
                    'top_cpu': top_cpu_processes,
                    'top_memory': top_memory_processes
                },
                'temperatures': temperatures,
                'boot_time': psutil.boot_time()
            }
            
            return metrics
            
        except Exception as e:
            print(f"Erro ao coletar métricas: {e}")
            return {}
    
    def _get_temperatures(self) -> Dict:
        """Tenta obter temperaturas do sistema."""
        try:
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                if temps:
                    result = {}
                    for name, entries in temps.items():
                        result[name] = [{'label': entry.label, 'current': entry.current} 
                                      for entry in entries if entry.current]
                    return result
        except:
            pass
        return {}
    
    def _get_top_processes_cpu(self, limit: int = 5) -> List[Dict]:
        """Obtém top processos por uso de CPU."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] and proc_info['cpu_percent'] > 0:
                        processes.append({
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'cpu_percent': proc_info['cpu_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:limit]
        except:
            return []
    
    def _get_top_processes_memory(self, limit: int = 5) -> List[Dict]:
        """Obtém top processos por uso de memória."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'memory_info']):
                try:
                    proc_info = proc.info
                    if proc_info['memory_percent'] and proc_info['memory_percent'] > 0:
                        processes.append({
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'memory_percent': proc_info['memory_percent'],
                            'memory_mb': proc_info['memory_info'].rss // (1024 * 1024)
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:limit]
        except:
            return []
    
    def add_metrics_to_history(self, metrics: Dict):
        """Adiciona métricas ao histórico."""
        self.history_data.append(metrics)
        
        # Manter apenas últimos 1000 registros
        if len(self.history_data) > 1000:
            self.history_data = self.history_data[-1000:]
        
        self._save_history()
    
    def get_metrics_in_range(self, hours: int = 24) -> List[Dict]:
        """Obtém métricas das últimas N horas."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered_metrics = []
        for metric in self.history_data:
            try:
                metric_time = datetime.fromisoformat(metric['timestamp'])
                if metric_time >= cutoff_time:
                    filtered_metrics.append(metric)
            except (ValueError, KeyError):
                continue
        
        return filtered_metrics
    
    def calculate_averages(self, hours: int = 24) -> Dict:
        """Calcula médias das métricas no período especificado."""
        metrics = self.get_metrics_in_range(hours)
        
        if not metrics:
            return {}
        
        total_count = len(metrics)
        cpu_sum = sum(m.get('cpu', {}).get('percent', 0) for m in metrics)
        memory_sum = sum(m.get('memory', {}).get('percent', 0) for m in metrics)
        disk_sum = sum(m.get('disk', {}).get('percent', 0) for m in metrics)
        
        return {
            'period_hours': hours,
            'sample_count': total_count,
            'averages': {
                'cpu_percent': cpu_sum / total_count if total_count > 0 else 0,
                'memory_percent': memory_sum / total_count if total_count > 0 else 0,
                'disk_percent': disk_sum / total_count if total_count > 0 else 0
            },
            'peaks': self._calculate_peaks(metrics)
        }
    
    def _calculate_peaks(self, metrics: List[Dict]) -> Dict:
        """Calcula picos de uso."""
        if not metrics:
            return {}
            
        cpu_values = [m.get('cpu', {}).get('percent', 0) for m in metrics]
        memory_values = [m.get('memory', {}).get('percent', 0) for m in metrics]
        disk_values = [m.get('disk', {}).get('percent', 0) for m in metrics]
        
        return {
            'cpu_max': max(cpu_values) if cpu_values else 0,
            'memory_max': max(memory_values) if memory_values else 0,
            'disk_max': max(disk_values) if disk_values else 0,
            'cpu_min': min(cpu_values) if cpu_values else 0,
            'memory_min': min(memory_values) if memory_values else 0,
            'disk_min': min(disk_values) if disk_values else 0
        }
    
    def start_monitoring(self, interval: int = 30):
        """Inicia monitoramento contínuo."""
        if self.monitoring:
            return False
            
        self.monitor_interval = interval
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        return True
    
    def stop_monitoring(self):
        """Para o monitoramento contínuo."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
    
    def _monitoring_loop(self):
        """Loop principal de monitoramento."""
        while self.monitoring:
            try:
                metrics = self.collect_current_metrics()
                if metrics:
                    self.add_metrics_to_history(metrics)
                time.sleep(self.monitor_interval)
            except Exception as e:
                print(f"Erro no monitoramento: {e}")
                time.sleep(5)  # Esperar um pouco antes de tentar novamente
    
    def generate_performance_report(self, hours: int = 24) -> Dict:
        """Gera relatório de performance detalhado."""
        metrics = self.get_metrics_in_range(hours)
        averages = self.calculate_averages(hours)
        
        if not metrics:
            return {'error': 'Nenhuma métrica disponível para o período'}
        
        # Análise de estabilidade
        cpu_values = [m.get('cpu', {}).get('percent', 0) for m in metrics]
        memory_values = [m.get('memory', {}).get('percent', 0) for m in metrics]
        
        cpu_variance = self._calculate_variance(cpu_values)
        memory_variance = self._calculate_variance(memory_values)
        
        # Detectar padrões de uso
        patterns = self._detect_usage_patterns(metrics)
        
        # Recomendações baseadas nos dados
        recommendations = self._generate_recommendations(averages, patterns)
        
        return {
            'period': f"Últimas {hours} horas",
            'sample_count': len(metrics),
            'averages': averages,
            'stability': {
                'cpu_variance': cpu_variance,
                'memory_variance': memory_variance,
                'stability_score': self._calculate_stability_score(cpu_variance, memory_variance)
            },
            'patterns': patterns,
            'recommendations': recommendations,
            'generated_at': datetime.now().isoformat()
        }
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calcula variância dos valores."""
        if len(values) < 2:
            return 0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    def _calculate_stability_score(self, cpu_var: float, memory_var: float) -> str:
        """Calcula score de estabilidade do sistema."""
        # Score baseado na variância (menor variância = mais estável)
        avg_variance = (cpu_var + memory_var) / 2
        
        if avg_variance < 50:
            return "Muito Estável"
        elif avg_variance < 150:
            return "Estável"
        elif avg_variance < 300:
            return "Moderadamente Instável"
        else:
            return "Instável"
    
    def _detect_usage_patterns(self, metrics: List[Dict]) -> Dict:
        """Detecta padrões de uso do sistema."""
        if len(metrics) < 10:
            return {}
        
        # Agrupar por hora do dia
        hourly_usage = {}
        for metric in metrics:
            try:
                hour = datetime.fromisoformat(metric['timestamp']).hour
                if hour not in hourly_usage:
                    hourly_usage[hour] = []
                
                hourly_usage[hour].append({
                    'cpu': metric.get('cpu', {}).get('percent', 0),
                    'memory': metric.get('memory', {}).get('percent', 0)
                })
            except:
                continue
        
        # Calcular médias por hora
        hourly_averages = {}
        for hour, usage_list in hourly_usage.items():
            cpu_avg = sum(u['cpu'] for u in usage_list) / len(usage_list)
            memory_avg = sum(u['memory'] for u in usage_list) / len(usage_list)
            hourly_averages[hour] = {'cpu': cpu_avg, 'memory': memory_avg}
        
        # Identificar picos de uso
        peak_hours = self._identify_peak_hours(hourly_averages)
        
        return {
            'hourly_averages': hourly_averages,
            'peak_hours': peak_hours,
            'usage_trend': self._calculate_usage_trend(metrics)
        }
    
    def _identify_peak_hours(self, hourly_averages: Dict) -> Dict:
        """Identifica horas de pico de uso."""
        if not hourly_averages:
            return {}
        
        cpu_values = [(hour, data['cpu']) for hour, data in hourly_averages.items()]
        memory_values = [(hour, data['memory']) for hour, data in hourly_averages.items()]
        
        cpu_peak = max(cpu_values, key=lambda x: x[1]) if cpu_values else (0, 0)
        memory_peak = max(memory_values, key=lambda x: x[1]) if memory_values else (0, 0)
        
        return {
            'cpu_peak_hour': cpu_peak[0],
            'cpu_peak_value': cpu_peak[1],
            'memory_peak_hour': memory_peak[0],
            'memory_peak_value': memory_peak[1]
        }
    
    def _calculate_usage_trend(self, metrics: List[Dict]) -> str:
        """Calcula tendência de uso (crescente, decrescente, estável)."""
        if len(metrics) < 5:
            return "Dados insuficientes"
        
        # Comparar primeira metade com segunda metade
        mid_point = len(metrics) // 2
        first_half = metrics[:mid_point]
        second_half = metrics[mid_point:]
        
        first_avg = sum(m.get('cpu', {}).get('percent', 0) for m in first_half) / len(first_half)
        second_avg = sum(m.get('cpu', {}).get('percent', 0) for m in second_half) / len(second_half)
        
        diff = second_avg - first_avg
        
        if diff > 5:
            return "Crescente"
        elif diff < -5:
            return "Decrescente"
        else:
            return "Estável"
    
    def _generate_recommendations(self, averages: Dict, patterns: Dict) -> List[str]:
        """Gera recomendações baseadas nas métricas."""
        recommendations = []
        
        avg_cpu = averages.get('averages', {}).get('cpu_percent', 0)
        avg_memory = averages.get('averages', {}).get('memory_percent', 0)
        
        # Recomendações baseadas em uso médio
        if avg_cpu > 80:
            recommendations.append("⚠️ CPU com uso muito alto. Considere fechar programas desnecessários.")
        elif avg_cpu > 60:
            recommendations.append("⚠️ CPU com uso alto. Monitor processos que consomem mais recursos.")
        
        if avg_memory > 85:
            recommendations.append("⚠️ Memória RAM crítica. Execute otimização de RAM urgentemente.")
        elif avg_memory > 70:
            recommendations.append("⚠️ Uso alto de memória. Considere otimização de RAM.")
        
        # Recomendações baseadas em padrões
        peak_hours = patterns.get('peak_hours', {})
        if peak_hours.get('cpu_peak_value', 0) > 90:
            hour = peak_hours.get('cpu_peak_hour', 0)
            recommendations.append(f"📊 Pico de CPU detectado às {hour}:00h. Evite tarefas pesadas nesse horário.")
        
        if not recommendations:
            recommendations.append("✅ Sistema operando dentro dos parâmetros normais.")
        
        return recommendations

    def cleanup_old_data(self, days: int = 7):
        """Remove dados antigos do histórico."""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        filtered_data = []
        for metric in self.history_data:
            try:
                metric_time = datetime.fromisoformat(metric['timestamp'])
                if metric_time >= cutoff_time:
                    filtered_data.append(metric)
            except (ValueError, KeyError):
                continue
        
        self.history_data = filtered_data
        self._save_history()
        
        return len(self.history_data)