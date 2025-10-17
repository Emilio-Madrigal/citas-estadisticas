from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict
from pruebaLocal import LocalDataProvider, citaData
import json

class MotorEstadisticas:
    def __init__(self, dentista_id: str):
        self.dentista_id = dentista_id
        self.citas: List[citaData] = []

    def cargar_citas(self, citas: List[citaData]):
        citas_validas = [
            c for c in citas 
            if c.dentista_id == self.dentista_id
        ]
        self.citas = citas_validas

    def filtrar_por_rango_fechas(
        self, 
        fecha_inicio: datetime, 
        fecha_fin: datetime
    ) -> List[citaData]:
        return [
            c for c in self.citas 
            if fecha_inicio <= c.cita_fecha <= fecha_fin
        ]

    def resumen_mensual(self, year: int, month: int) -> Dict:
        fecha_inicio = datetime(year, month, 1)
        fecha_fin = datetime(year, month + 1, 1) - timedelta(days=1) if month < 12 else datetime(year + 1, 1, 1) - timedelta(days=1)

        citas_mes = self.filtrar_por_rango_fechas(fecha_inicio, fecha_fin)

        citas_completadas = [c for c in citas_mes if c.estado == 'completada']
        citas_canceladas = [c for c in citas_mes if c.estado == 'cancelada']

        pacientes_unicos = len(set(c.paciente_id for c in citas_completadas))
        ingresos_totales = sum(c.monto for c in citas_completadas)
        total_citas = len(citas_mes)
        tasa_cancelacion = (len(citas_canceladas) / total_citas * 100) if total_citas > 0 else 0

        calificaciones = [c.calificacion for c in citas_completadas if c.calificacion is not None]
        calificacion_promedio = sum(calificaciones)/len(calificaciones) if calificaciones else 0

        return {
            'periodo': f'{year}-{month:02d}',
            'total_citas': total_citas,
            'citas_completadas': len(citas_completadas),
            'citas_canceladas': len(citas_canceladas),
            'pacientes_unicos': pacientes_unicos,
            'ingresos_totales': round(ingresos_totales, 2),
            'tasa_cancelacion': round(tasa_cancelacion, 2),
            'calificacion_promedio': round(calificacion_promedio, 2)
        }

    def distribucion_servicios(self, fecha_inicio: datetime, fecha_fin: datetime) -> Dict[str, int]:
        citas_periodo = self.filtrar_por_rango_fechas(fecha_inicio, fecha_fin)
        distribucion = defaultdict(int)
        for c in citas_periodo:
            if c.estado == 'completada':
                distribucion[c.nombre_servicio] += 1
        return dict(distribucion)

    def ingresos_por_pago(self, fecha_inicio: datetime, fecha_fin: datetime) -> Dict[str, float]:
        citas_periodo = self.filtrar_por_rango_fechas(fecha_inicio, fecha_fin)
        ingresos = defaultdict(float)
        for c in citas_periodo:
            if c.estado == 'completada':
                ingresos[c.metodo_pago] += c.monto
        return {metodo: round(monto, 2) for metodo, monto in ingresos.items()}

    def carga_por_dia(self, fecha_inicio: datetime, fecha_fin: datetime) -> Dict[str, float]:
        citas_periodo = self.filtrar_por_rango_fechas(fecha_inicio, fecha_fin)
        dias_semana = ['Lunes','Martes','Miercoles','Jueves','Viernes','Sabado','Domingo']
        citas_por_dia = defaultdict(int)
        for c in citas_periodo:
            if c.estado == 'completada':
                dia = dias_semana[c.cita_fecha.weekday()]
                citas_por_dia[dia] += 1
        total_dias = (fecha_fin - fecha_inicio).days + 1
        total_semanas = total_dias / 7
        return {dia: round(citas_por_dia[dia]/total_semanas,2) if total_semanas>0 else 0 for dia in dias_semana}

    def pacientes_nuevos_vs_recurrentes(self, fecha_inicio: datetime, fecha_fin: datetime) -> Dict:
        citas_ordenadas = sorted(self.citas, key=lambda c: c.cita_fecha)
        primera_cita = {}
        for c in citas_ordenadas:
            if c.paciente_id not in primera_cita:
                primera_cita[c.paciente_id] = c.cita_fecha
        citas_periodo = self.filtrar_por_rango_fechas(fecha_inicio, fecha_fin)
        nuevos = 0
        recurrentes = 0
        pacientes_analizados = set()
        for c in citas_periodo:
            if c.estado != 'completada':
                continue
            if c.paciente_id in pacientes_analizados:
                continue
            pacientes_analizados.add(c.paciente_id)
            if primera_cita[c.paciente_id] >= fecha_inicio:
                nuevos += 1
            else:
                recurrentes += 1
        return {'nuevos': nuevos, 'recurrentes': recurrentes, 'total': nuevos+recurrentes}

    def servicios_mas_solicitados(self, fecha_inicio: datetime, fecha_fin: datetime, limite: int =5) -> List[Dict]:
        distribucion = self.distribucion_servicios(fecha_inicio, fecha_fin)
        ordenados = sorted(distribucion.items(), key=lambda x:x[1], reverse=True)
        top = ordenados[:limite]
        return [{'servicio': s, 'cantidad': c} for s,c in top]

    def comparar_periodos(self, inicio1: datetime, fin1: datetime, inicio2: datetime, fin2: datetime) -> Dict:
        citas1 = [c for c in self.filtrar_por_rango_fechas(inicio1, fin1) if c.estado=='completada']
        citas2 = [c for c in self.filtrar_por_rango_fechas(inicio2, fin2) if c.estado=='completada']
        ingresos1 = sum(c.monto for c in citas1)
        ingresos2 = sum(c.monto for c in citas2)

        def crecimiento(viejo, nuevo):
            if viejo==0: return 100.0 if nuevo>0 else 0.0
            return ((nuevo-viejo)/viejo)*100

        return {
            'periodo_1': {'citas': len(citas1), 'ingresos': round(ingresos1,2)},
            'periodo_2': {'citas': len(citas2), 'ingresos': round(ingresos2,2)},
            'crecimiento': {
                'citas_porcentaje': round(crecimiento(len(citas1), len(citas2)),2),
                'ingresos_porcentaje': round(crecimiento(ingresos1, ingresos2),2)
            }
        }

    def generar_reporte_completo(self, year:int, month:int) -> str:
        fecha_inicio = datetime(year, month, 1)
        fecha_fin = datetime(year, month+1, 1) - timedelta(days=1) if month<12 else datetime(year+1,1,1) - timedelta(days=1)

        reporte = {
            'dentista_id': self.dentista_id,
            'periodo_reporte': f'{year}-{month:02d}',
            'generado_en': datetime.now().isoformat(),
            'resumen_mensual': self.resumen_mensual(year, month),
            'distribucion_servicios': self.distribucion_servicios(fecha_inicio, fecha_fin),
            'ingresos_por_pago': self.ingresos_por_pago(fecha_inicio, fecha_fin),
            'carga_por_dia': self.carga_por_dia(fecha_inicio, fecha_fin),
            'pacientes_analisis': self.pacientes_nuevos_vs_recurrentes(fecha_inicio, fecha_fin),
            'top_servicios': self.servicios_mas_solicitados(fecha_inicio, fecha_fin)
        }

        return json.dumps(reporte, indent=2, ensure_ascii=False)


def main():
    
    dentist_id = "dentist_001"
    
    print("inicializando sistema de estadisticas...")
    engine = MotorEstadisticas(dentist_id)
    
    print("generando datos de prueba...")
    appointments = LocalDataProvider.generar_citas(
        dentista_id=dentist_id,
        total_citas=150,
        months_back=6
    )
    
    print(f"cargando {len(appointments)} citas...")
    engine.cargar_citas(appointments)
    
    current_date = datetime.now()
    
    print("\ngenerando reporte mensual...")
    report = engine.generar_reporte_completo(current_date.year, current_date.month)
    print(report)
    
    print("\nguardando datos locales...")
    LocalDataProvider.save_to_json(appointments, "local_appointments.json")
    print("datos guardados en: local_appointments.json")


if __name__ == "__main__":
    main()