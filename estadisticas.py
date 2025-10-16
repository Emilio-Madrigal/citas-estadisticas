from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from pruebaLocal import LocalDataProvider, AppointmentData
import json

class StatisticsEngine:
    def __init__(self, dentist_id: str):
        self.dentist_id = dentist_id
        self.appointments: List[AppointmentData] = []
    
    def load_appointments(self, appointments: List[AppointmentData]):
        valid_appointments = [
            apt for apt in appointments 
            if apt.dentist_id == self.dentist_id
        ]
        self.appointments = valid_appointments
    
    def filter_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[AppointmentData]:
        return [
            apt for apt in self.appointments 
            if start_date <= apt.appointment_date <= end_date
        ]
    
    def calculate_monthly_summary(self, year: int, month: int) -> Dict:
        start_date = datetime(year, month, 1)
        
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        monthly_appointments = self.filter_by_date_range(start_date, end_date)
        
        completed_appointments = [
            apt for apt in monthly_appointments 
            if apt.status == 'completada'
        ]
        
        canceled_appointments = [
            apt for apt in monthly_appointments 
            if apt.status == 'cancelada'
        ]
        
        unique_patients = len(set(
            apt.patient_id for apt in completed_appointments
        ))
        
        total_revenue = sum(apt.amount for apt in completed_appointments)
        
        total_appointments = len(monthly_appointments)
        cancellation_rate = (
            len(canceled_appointments) / total_appointments * 100 
            if total_appointments > 0 else 0
        )
        
        ratings = [
            apt.rating for apt in completed_appointments 
            if apt.rating is not None
        ]
        average_rating = (
            sum(ratings) / len(ratings) 
            if ratings else 0
        )
        
        return {
            'period': f'{year}-{month:02d}',
            'total_appointments': total_appointments,
            'completed_appointments': len(completed_appointments),
            'canceled_appointments': len(canceled_appointments),
            'unique_patients': unique_patients,
            'total_revenue': round(total_revenue, 2),
            'cancellation_rate': round(cancellation_rate, 2),
            'average_rating': round(average_rating, 2)
        }
    
    def service_distribution(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, int]:
        period_appointments = self.filter_by_date_range(start_date, end_date)
        distribution = defaultdict(int)
        
        for appointment in period_appointments:
            if appointment.status == 'completada':
                distribution[appointment.service_name] += 1
        
        return dict(distribution)
    
    def revenue_by_payment_method(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, float]:
        period_appointments = self.filter_by_date_range(start_date, end_date)
        revenue = defaultdict(float)
        
        for appointment in period_appointments:
            if appointment.status == 'completada':
                revenue[appointment.payment_method] += appointment.amount
        
        return {
            method: round(amount, 2) 
            for method, amount in revenue.items()
        }
    
    def workload_by_weekday(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, float]:
        period_appointments = self.filter_by_date_range(start_date, end_date)
        
        weekday_names = [
            'Lunes', 'Martes', 'Miercoles', 
            'Jueves', 'Viernes', 'Sabado', 'Domingo'
        ]
        
        appointments_per_day = defaultdict(int)
        
        for appointment in period_appointments:
            if appointment.status == 'completada':
                day_name = weekday_names[appointment.appointment_date.weekday()]
                appointments_per_day[day_name] += 1
        
        total_days = (end_date - start_date).days + 1
        total_weeks = total_days / 7
        
        average_workload = {
            day: round(appointments_per_day[day] / total_weeks, 2) 
            if total_weeks > 0 else 0
            for day in weekday_names
        }
        
        return average_workload
    
    def new_vs_returning_patients(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict:
        all_appointments_sorted = sorted(
            self.appointments, 
            key=lambda a: a.appointment_date
        )
        
        first_appointment_date = {}
        
        for appointment in all_appointments_sorted:
            if appointment.patient_id not in first_appointment_date:
                first_appointment_date[appointment.patient_id] = appointment.appointment_date
        
        period_appointments = self.filter_by_date_range(start_date, end_date)
        new_patients = 0
        returning_patients = 0
        
        analyzed_patients = set()
        
        for appointment in period_appointments:
            if appointment.status == 'completada':
                patient_id = appointment.patient_id
                
                if patient_id in analyzed_patients:
                    continue
                
                analyzed_patients.add(patient_id)
                
                if first_appointment_date[patient_id] >= start_date:
                    new_patients += 1
                else:
                    returning_patients += 1
        
        return {
            'new_patients': new_patients,
            'returning_patients': returning_patients,
            'total_patients': new_patients + returning_patients
        }
    
    def top_requested_services(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        limit: int = 5
    ) -> List[Dict]:
        distribution = self.service_distribution(start_date, end_date)
        
        sorted_services = sorted(
            distribution.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        top_services = sorted_services[:limit]
        
        return [
            {'service': service, 'count': count}
            for service, count in top_services
        ]
    
    def compare_periods(
        self,
        period1_start: datetime,
        period1_end: datetime,
        period2_start: datetime,
        period2_end: datetime
    ) -> Dict:
        period1_appointments = self.filter_by_date_range(period1_start, period1_end)
        period2_appointments = self.filter_by_date_range(period2_start, period2_end)
        
        period1_completed = [
            apt for apt in period1_appointments 
            if apt.status == 'completada'
        ]
        period2_completed = [
            apt for apt in period2_appointments 
            if apt.status == 'completada'
        ]
        
        period1_revenue = sum(apt.amount for apt in period1_completed)
        period2_revenue = sum(apt.amount for apt in period2_completed)
        
        def calculate_growth(old_value, new_value):
            if old_value == 0:
                return 100.0 if new_value > 0 else 0.0
            return ((new_value - old_value) / old_value) * 100
        
        return {
            'period_1': {
                'appointments': len(period1_completed),
                'revenue': round(period1_revenue, 2)
            },
            'period_2': {
                'appointments': len(period2_completed),
                'revenue': round(period2_revenue, 2)
            },
            'growth': {
                'appointments_percentage': round(
                    calculate_growth(
                        len(period1_completed), 
                        len(period2_completed)
                    ), 2
                ),
                'revenue_percentage': round(
                    calculate_growth(period1_revenue, period2_revenue), 2
                )
            }
        }
    
    def generate_complete_report(self, year: int, month: int) -> str:
        start_date = datetime(year, month, 1)
        
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        report = {
            'dentist_id': self.dentist_id,
            'report_period': f'{year}-{month:02d}',
            'generated_at': datetime.now().isoformat(),
            'monthly_summary': self.calculate_monthly_summary(year, month),
            'service_distribution': self.service_distribution(start_date, end_date),
            'revenue_by_payment': self.revenue_by_payment_method(start_date, end_date),
            'workload_analysis': self.workload_by_weekday(start_date, end_date),
            'patient_analysis': self.new_vs_returning_patients(start_date, end_date),
            'top_services': self.top_requested_services(start_date, end_date)
        }
        
        return json.dumps(report, indent=2, ensure_ascii=False)


def main():
    
    dentist_id = "dentist_001"
    
    print("Inicializando sistema de estadisticas...")
    engine = StatisticsEngine(dentist_id)
    
    print("Generando datos de prueba...")
    appointments = LocalDataProvider.generate_appointments(
        dentist_id=dentist_id,
        total_appointments=150,
        months_back=6
    )
    
    print(f"Cargando {len(appointments)} citas...")
    engine.load_appointments(appointments)
    
    current_date = datetime.now()
    
    print("\nGenerando reporte mensual...")
    report = engine.generate_complete_report(current_date.year, current_date.month)
    print(report)
    
    print("\nGuardando datos locales...")
    LocalDataProvider.save_to_json(appointments, "local_appointments.json")
    print("Datos guardados en: local_appointments.json")


if __name__ == "__main__":
    main()