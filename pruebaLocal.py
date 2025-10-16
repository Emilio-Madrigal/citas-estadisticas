import random
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json

@dataclass
class AppointmentData:
    appointment_id: str
    patient_id: str
    patient_name: str
    dentist_id: str
    office_id: str
    appointment_date: datetime
    service_name: str
    duration_minutes: int
    amount: float
    payment_method: str
    status: str
    rating: Optional[float] = None


class LocalDataProvider:
    PATIENT_FIRST_NAMES = [
        "Roberto", "Patricia", "Miguel", "Elena", "Fernando", 
        "Isabel", "Ricardo", "Monica", "Alejandro", "Claudia",
        "Daniel", "Beatriz", "Jorge", "Silvia", "Raul"
    ]
    
    PATIENT_LAST_NAMES = [
        "Hernandez", "Martinez", "Lopez", "Gonzalez", "Perez",
        "Sanchez", "Ramirez", "Torres", "Flores", "Rivera"
    ]
    
    SERVICE_CATALOG = [
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
    
    OFFICE_IDS = ["office_alpha", "office_beta", "office_gamma"]
    PAYMENT_METHODS = ["efectivo", "stripe", "transferencia"]
    STATUS_OPTIONS = ["completada", "cancelada", "pendiente"]
    
    @staticmethod
    def generate_full_name() -> str:
        first_name = random.choice(LocalDataProvider.PATIENT_FIRST_NAMES)
        last_name = random.choice(LocalDataProvider.PATIENT_LAST_NAMES)
        return f"{first_name} {last_name}"
    
    @staticmethod
    def generate_appointments(
        dentist_id: str, 
        total_appointments: int = 100,
        months_back: int = 6
    ) -> List[AppointmentData]:
        appointments = []
        current_date = datetime.now()
        registered_patients = {}
        
        for appointment_number in range(total_appointments):
            days_ago = random.randint(0, months_back * 30)
            hour = random.randint(8, 18)
            minute = random.choice([0, 30])
            
            appointment_datetime = current_date - timedelta(days=days_ago)
            appointment_datetime = appointment_datetime.replace(
                hour=hour, 
                minute=minute, 
                second=0, 
                microsecond=0
            )
            
            if registered_patients and random.random() < 0.3:
                patient_id = random.choice(list(registered_patients.keys()))
                patient_name = registered_patients[patient_id]
            else:
                patient_id = f"patient_{len(registered_patients) + 1:04d}"
                patient_name = LocalDataProvider.generate_full_name()
                registered_patients[patient_id] = patient_name
            
            service_name, duration, base_amount = random.choice(
                LocalDataProvider.SERVICE_CATALOG
            )
            
            price_variation = random.uniform(0.9, 1.1)
            final_amount = round(base_amount * price_variation, 2)
            
            probability = random.random()
            if probability < 0.85:
                appointment_status = "completada"
                appointment_rating = round(random.uniform(3.5, 5.0), 1)
            elif probability < 0.95:
                appointment_status = "cancelada"
                appointment_rating = None
            else:
                appointment_status = "pendiente"
                appointment_rating = None
            
            appointment = AppointmentData(
                appointment_id=f"appt_{appointment_number + 1:04d}",
                patient_id=patient_id,
                patient_name=patient_name,
                dentist_id=dentist_id,
                office_id=random.choice(LocalDataProvider.OFFICE_IDS),
                appointment_date=appointment_datetime,
                service_name=service_name,
                duration_minutes=duration,
                amount=final_amount,
                payment_method=random.choice(LocalDataProvider.PAYMENT_METHODS),
                status=appointment_status,
                rating=appointment_rating
            )
            
            appointments.append(appointment)
        
        appointments.sort(key=lambda a: a.appointment_date)
        return appointments
    
    @staticmethod
    def load_from_json(file_path: str) -> List[AppointmentData]:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        appointments = []
        for item in data:
            item['appointment_date'] = datetime.fromisoformat(item['appointment_date'])
            appointments.append(AppointmentData(**item))
        
        return appointments
    
    @staticmethod
    def save_to_json(appointments: List[AppointmentData], file_path: str):
        data = []
        for appointment in appointments:
            appointment_dict = asdict(appointment)
            appointment_dict['appointment_date'] = appointment.appointment_date.isoformat()
            data.append(appointment_dict)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
