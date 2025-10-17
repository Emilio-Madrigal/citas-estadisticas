import random
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json

@dataclass
class citaData:
    cita_id: str
    paciente_id: str
    nombre_paciente: str
    dentista_id: str
    consultorio_id: str
    cita_fecha: datetime
    nombre_servicio: str
    duracion_min: int
    monto: float
    metodo_pago: str
    estado: str
    calificacion: Optional[float] = None


class LocalDataProvider:
    nombres = [
        "Roberto", "Patricia", "Miguel", "Elena", "Fernando", 
        "Isabel", "Ricardo", "Monica", "Alejandro", "Claudia",
        "Daniel", "Beatriz", "Jorge", "Silvia", "Raul"
    ]
    
    apellidos = [
        "Hernandez", "Martinez", "Lopez", "Gonzalez", "Perez",
        "Sanchez", "Ramirez", "Torres", "Flores", "Rivera"
    ]
    
    servicios = [
        ("Limpieza dental", 45, 800),
        ("Ortodoncia", 60, 2500),
        ("Extraccion simple", 30, 1200),
        ("Blanqueamiento dental", 90, 3500),
        ("Endodoncia", 120, 4000),
        ("Implante dental", 180, 15000),
        ("Revision general", 30, 500),
        ("Resina dental", 60, 1500),
        ("Corona dental", 90, 8000),
        ("Puente dental", 120, 12000),
    ]
    
    consultorio_id = ["office_alpha", "office_beta", "office_gamma"]
    metodos_pago = ["efectivo", "stripe", "transferencia"]
    estados = ["completada", "cancelada", "pendiente"]
    
    @staticmethod
    def generar_nombre_completo() -> str:
        nombre = random.choice(LocalDataProvider.nombres)
        apellido = random.choice(LocalDataProvider.apellidos)
        return f"{nombre} {apellido}"
    
    @staticmethod
    def generar_citas(
        dentista_id: str, 
        total_citas: int = 100,
        months_back: int = 6
    ) -> List[citaData]:
        citas = []
        fecha_actual = datetime.now()
        pacientes_r = {}
        
        for numero_cita in range(total_citas):
            days_ago = random.randint(0, months_back * 30)
            hora = random.randint(8, 18)
            minuto = random.choice([0, 30])
            
            cita_datetime = fecha_actual - timedelta(days=days_ago)
            cita_datetime = cita_datetime.replace(
                hour=hora, 
                minute=minuto, 
                second=0, 
                microsecond=0
            )
            
            if pacientes_r and random.random() < 0.3:
                paciente_id = random.choice(list(pacientes_r.keys()))
                paciente_nombre = pacientes_r[paciente_id]
            else:
                paciente_id = f"patient_{len(pacientes_r) + 1:04d}"
                paciente_nombre = LocalDataProvider.generar_nombre_completo()
                pacientes_r[paciente_id] = paciente_nombre
            
            nombre_servicio, duracion, monto_base = random.choice(
                LocalDataProvider.servicios
            )
            
            variacion_p = random.uniform(0.9, 1.1)
            monto_final = round(monto_base * variacion_p, 2)
            
            p = random.random()
            if p < 0.85:
                estado_cita = "completada"
                cita_calif = round(random.uniform(3.5, 5.0), 1)
            elif p < 0.95:
                estado_cita = "cancelada"
                cita_calif = None
            else:
                estado_cita = "pendiente"
                cita_calif = None
            
            cita = citaData(
                cita_id=f"cita_{numero_cita + 1:04d}",
                paciente_id=paciente_id,
                nombre_paciente=paciente_nombre,
                dentista_id=dentista_id,
                consultorio_id=random.choice(LocalDataProvider.consultorio_id),
                cita_fecha=cita_datetime,
                nombre_servicio=nombre_servicio,
                duracion_min=duracion,
                monto=monto_final,
                metodo_pago=random.choice(LocalDataProvider.metodos_pago),
                estado=estado_cita,
                calificacion=cita_calif
            )
            
            citas.append(cita)
        
        citas.sort(key=lambda a: a.cita_fecha)
        return citas
    
    @staticmethod
    def load_from_json(file_path: str) -> List[citaData]:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        citas = []
        for item in data:
            item['cita_fecha'] = datetime.fromisoformat(item['cita_fecha'])
            citas.append(citaData(**item))
        
        return citas
    
    @staticmethod
    def save_to_json(citas: List[citaData], file_path: str):
        data = []
        for cita in citas:
            cita_dict = asdict(cita)
            cita_dict['cita_fecha'] = cita.cita_fecha.isoformat()
            data.append(cita_dict)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
