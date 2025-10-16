from datetime import datetime,timedelta
from typing import Dict,List,Optional,Tuple
from dataclasses import dataclass,asdict
from collections import defaultdict
import json
import random

@dataclass
class CitaData:
    cita_id:str
    paciente_id:str
    paciente_name:str
    dentista_id:str
    consultorio_id:str
    cita_date:datetime
    servicio_type:str
    duracion_minutos:int
    costo:float
    metodo_pago:str
    estado:str
    rating:Optional[float] = None

class prueba:
    nombres_pacientes = [
        "Roberto", "Patricia", "Miguel", "Elena", "Fernando", 
        "Isabel", "Ricardo", "Monica", "Alejandro", "Claudia",
        "Daniel", "Beatriz", "Jorge", "Silvia", "Raul"
    ]
    
    apellidos_pacientes = [
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
    
    consultorio_id = ["alpharius", "omegon", "legion alpha"]
    metodos_pago = ["efectivo", "stripe", "transferencia"]
    estados = ["completada", "cancelada", "pendiente"]

    def nombre_completo()->str:
        nombre=random.choice(prueba.nombres_pacientes)
        apellido=random.choice(prueba.apellidos_pacientes)
        return f"{nombre} {apellido}"
    def citas(dentista_id:str,total_citas:int=100,hace:int=6"""meses""" )-> List[citasData]:
        citas=[]
        fecha_actual=datetime.now()
        pacientes={}

        for numero_Citas in range(total_citas):
            dias=random.randint(0,hace*30)
            hora=random.randint(8,18)
            minuto=random.choice([0,30])



    