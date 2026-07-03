# analyzer.py
import json
import csv
from datetime import datetime
from collections import Counter, defaultdict
from pathlib import Path
import sys

class DetectionAnalyzer:
    """Analizador de Analítica Vehicular Empresarial (VisionX Data Engine)"""

    def __init__(self, json_file):
        """
        Inicializa el motor analítico con un archivo de logs JSON.
        """
        self.json_file = Path(json_file)
        self.detections = []
        self.load_data()

    def load_data(self):
        """Carga y normaliza los datos del archivo JSON"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.detections = json.load(f)
            print(f"📦 [Data Engine] Carga exitosa: {len(self.detections)} registros detectados.")
        except FileNotFoundError:
            print(f"❌ [Error] El archivo especificado no existe: {self.json_file}")
            self.detections = []
        except json.JSONDecodeError:
            print(f"❌ [Error] El archivo no cuenta con un formato JSON válido.")
            self.detections = []

    def get_statistics(self):
        """Calcula el set completo de métricas e indicadores de tráfico"""
        if not self.detections:
            return None

        classes = [d['class'] for d in self.detections]
        confidences = [d.get('confidence', 0.0) for d in self.detections if 'confidence' in d]

        # Agrupación por Horas (Línea de tiempo detallada)
        hourly_distribution = defaultdict(int)
        for d in self.detections:
            # Soporta formato ISO largo o formato HH:MM:SS nativo del streaming
            t_str = d.get('timestamp' if 'timestamp' in d else 'time', '00:00')
            try:
                # Extrae el componente de la hora
                hour = t_str.split('T')[1][:2] if 'T' in t_str else t_str[:2]
                hourly_distribution[f"{hour}:00 hrs"] += 1
            except IndexError:
                hourly_distribution["Desconocido"] += 1

        # Identificar la hora pico de tráfico
        peak_hour = "N/A"
        if hourly_distribution:
            peak_hour = max(hourly_distribution, key=hourly_distribution.get)

        stats = {
            'total_detections': len(self.detections),
            'unique_classes_count': len(set(classes)),
            'class_distribution': dict(Counter(classes)),
            'hourly_distribution': dict(hourly_distribution),
            'peak_traffic_hour': peak_hour,
            'confidence_metrics': {
                'avg': sum(confidences) / len(confidences) if confidences else 0.0,
                'min': min(confidences) if confidences else 0.0,
                'max': max(confidences) if confidences else 0.0
            }
        }
        return stats

    def print_dashboard(self):
        """Despliega un reporte ejecutivo analítico directo en la terminal"""
        stats = self.get_statistics()
        if not stats:
            print("⚠️ No existen suficientes datos analíticos para generar el reporte.")
            return

        print("\n" + "═"*60)
        print(" 📊 INFORME EJECUTIVO DE TRÁFICO - VISIONX ANALYTICS")
        print("═"*60)
        print(f" Total vehículos procesados : {stats['total_detections']}")
        print(f" Categorías distintas       : {stats['unique_classes_count']}")
        print(f" Hora de mayor flujo (Pico) : {stats['peak_traffic_hour']}")

        if stats['confidence_metrics']['avg'] > 0:
            conf = stats['confidence_metrics']
            print(f" Fiabilidad Promedio IA    : {conf['avg']:.2%}")
            print(f" Rango de Confianza        : [{conf['min']:.1%} - {conf['max']:.1%}]")

        print("\n 🚗 Flujo Volumétrico por Categoría:")
        print("─"*60)
        for cl, count in sorted(stats['class_distribution'].items(), key=lambda x: x[1], reverse=True):
            pct = (count / stats['total_detections']) * 100
            bar = "■" * int(pct // 5)
            print(f"  {cl.upper():<12} | {count:>4} uds ({pct:>5.1f}%) {bar}")

        print("\n ⏱️ Distribución de Tránsito por Franja Horaria:")
        print("─"*60)
        for hr, count in sorted(stats['hourly_distribution'].items()):
            bar_hr = "█" * min(count, 30)  # Limitar largo visual en consola
            print(f"  {hr:<12} | {count:>4} pasadas  {bar_hr}")
        print("═"*60 + "\n")

    def export_to_csv(self, output_path=None):
        """Exporta los registros estructurados a un formato CSV estandarizado"""
        if not self.detections:
            return

        if not output_path:
            output_path = self.json_file.with_suffix('.csv')

        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                # Soporte dinámico si el log viene extendido con cajas de coordenadas o simplificado de la web
                has_boxes = 'box' in self.detections[0]
                fieldnames = ['time_stamp', 'vehicle_class', 'confidence']
                if has_boxes:
                    fieldnames.extend(['x1', 'y1', 'x2', 'y2'])

                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for d in self.detections:
                    t_val = d.get('timestamp' if 'timestamp' in d else 'time', 'N/A')
                    row = {
                        'time_stamp': t_val,
                        'vehicle_class': d['class'],
                        'confidence': d.get('confidence', 1.0)
                    }
                    if has_boxes and 'box' in d:
                        row.update({
                            'x1': d['box'][0], 'y1': d['box'][1],
                            'x2': d['box'][2], 'y2': d['box'][3]
                        })
                    writer.writerow(row)

            print(f"✅ Data exportada exitosamente a formato CSV: {output_path}")
        except Exception as e:
            print(f"❌ Error durante el volcado de datos a CSV: {e}")

    def generate_json_summary(self, output_path=None):
        """Genera un reporte consolidado automatizado en formato JSON estructurado"""
        if not self.detections:
            return

        if not output_path:
            output_path = self.json_file.parent / f"resumen_analitico_{self.json_file.name}"

        report = {
            'metadata': {
                'timestamp_generacion': datetime.now().isoformat(),
                'archivo_origen': str(self.json_file.name),
            },
            'metrics': self.get_statistics()
        }

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=4, ensure_ascii=False)
            print(f"✅ Compilado estratégico guardado: {output_path}")
        except Exception as e:
            print(f"❌ Error al consolidar el archivo JSON: {e}")

def main():
    """Punto de entrada de ejecución inteligente para análisis de datos"""
    # Escanear el directorio local buscando archivos autogenerados por el detector anterior
    json_files = sorted(list(Path('.').glob('detecciones_*.json')))

    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    elif json_files:
        target_file = json_files[-1]  # Toma el archivo más reciente de forma automática
    else:
        print("❌ No se detectó ningún archivo de datos local (Formato esperado: detecciones_*.json)")
        print("💡 Consejo: Ejecuta e inicia detecciones en tu servidor web primero.")
        return

    analyzer = DetectionAnalyzer(target_file)
    analyzer.print_dashboard()
    analyzer.export_to_csv()
    analyzer.generate_json_summary()

if __name__ == '__main__':
    main()
