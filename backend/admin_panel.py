from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging
from dataclasses import dataclass
from enum import Enum
import asyncio
from daticos_extractor import daticos_extractor

logger = logging.getLogger(__name__)

class ExtractionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DataSource(str, Enum):
    DATICOS_ORIGINAL = "daticos_original"
    LOCAL_DATABASE = "local_database"
    TSE = "tse"
    REGISTRO_NACIONAL = "registro_nacional"
    CREDISERVER = "crediserver"
    GOOGLE_MAPS = "google_maps"

@dataclass
class ExtractionTask:
    task_id: str
    source: DataSource
    status: ExtractionStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    records_extracted: int = 0
    total_records: Optional[int] = None
    error_message: Optional[str] = None
    progress_percentage: float = 0.0

class AdminPanelModels:
    """Modelos Pydantic para el panel de administración"""
    
    class SystemStats(BaseModel):
        total_personas_fisicas: int
        total_personas_juridicas: int
        total_provincias: int
        total_cantones: int
        total_distritos: int
        data_sources_summary: Dict[str, int]
        last_update: Optional[datetime]
        database_size_mb: float
        active_extraction_tasks: int
        
    class ExtractionTaskModel(BaseModel):
        task_id: str
        source: DataSource
        status: ExtractionStatus
        created_at: datetime
        started_at: Optional[datetime] = None
        completed_at: Optional[datetime] = None
        records_extracted: int = 0
        total_records: Optional[int] = None
        error_message: Optional[str] = None
        progress_percentage: float = 0.0
    
    class StartExtractionRequest(BaseModel):
        source: DataSource
        limit: Optional[int] = 1000
        extraction_type: str = "full"  # full, incremental, specific
        specific_criteria: Optional[Dict[str, Any]] = None
        
    class DatabaseAnalysis(BaseModel):
        data_quality_score: float
        completeness_by_field: Dict[str, float]
        duplicate_records: int
        missing_critical_fields: int
        geographic_coverage: Dict[str, int]
        temporal_distribution: Dict[str, int]
        
    class UserManagement(BaseModel):
        user_id: str
        username: str
        full_name: str
        email: str
        role: str
        is_active: bool
        last_login: Optional[datetime]
        total_queries: int
        created_at: datetime

class AdminPanelManager:
    """Gestor del panel de administración"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.active_tasks: Dict[str, ExtractionTask] = {}
        
    async def get_system_statistics(self) -> AdminPanelModels.SystemStats:
        """Obtener estadísticas completas del sistema"""
        try:
            # Conteos básicos
            total_fisicas = await self.db.personas_fisicas.count_documents({})
            total_juridicas = await self.db.personas_juridicas.count_documents({})
            total_provincias = await self.db.provincias.count_documents({})
            total_cantones = await self.db.cantones.count_documents({})
            total_distritos = await self.db.distritos.count_documents({})
            
            # Resumen por fuentes de datos
            data_sources = {}
            for source in DataSource:
                fisicas_count = await self.db.personas_fisicas.count_documents(
                    {"fuente_datos": source.value}
                )
                juridicas_count = await self.db.personas_juridicas.count_documents(
                    {"fuente_datos": source.value}
                )
                data_sources[source.value] = fisicas_count + juridicas_count
            
            # Última actualización
            last_update_record = await self.db.update_statistics.find_one(
                {}, sort=[("timestamp", -1)]
            )
            last_update = last_update_record['timestamp'] if last_update_record else None
            
            # Tamaño de base de datos (aproximado)
            stats = await self.db.command("dbstats")
            db_size_mb = stats.get('dataSize', 0) / (1024 * 1024)
            
            return AdminPanelModels.SystemStats(
                total_personas_fisicas=total_fisicas,
                total_personas_juridicas=total_juridicas,
                total_provincias=total_provincias,
                total_cantones=total_cantones,
                total_distritos=total_distritos,
                data_sources_summary=data_sources,
                last_update=last_update,
                database_size_mb=round(db_size_mb, 2),
                active_extraction_tasks=len([t for t in self.active_tasks.values() 
                                           if t.status == ExtractionStatus.IN_PROGRESS])
            )
            
        except Exception as e:
            logger.error(f"Error getting system statistics: {e}")
            raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")
    
    async def start_daticos_extraction(self, request: AdminPanelModels.StartExtractionRequest) -> str:
        """Iniciar extracción de datos del Daticos original"""
        task_id = f"extract_{request.source.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        task = ExtractionTask(
            task_id=task_id,
            source=request.source,
            status=ExtractionStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        self.active_tasks[task_id] = task
        
        # Ejecutar extracción en background
        asyncio.create_task(self._execute_daticos_extraction(task, request))
        
        logger.info(f"🚀 Tarea de extracción iniciada: {task_id}")
        return task_id
    
    async def _execute_daticos_extraction(self, task: ExtractionTask, request: AdminPanelModels.StartExtractionRequest):
        """Ejecutar la extracción de datos de Daticos en background"""
        try:
            task.status = ExtractionStatus.IN_PROGRESS
            task.started_at = datetime.utcnow()
            
            # Realizar login en Daticos
            logger.info(f"🔐 Iniciando login en Daticos para tarea {task.task_id}")
            login_success = await daticos_extractor.login()
            
            if not login_success:
                raise Exception("No se pudo realizar login en Daticos.com")
            
            task.progress_percentage = 10.0
            
            # Analizar estructura del sistema
            logger.info(f"🔍 Analizando estructura del sistema Daticos")
            system_structure = await daticos_extractor.discover_system_structure()
            
            # Guardar análisis del sistema
            await self.db.system_analysis.insert_one({
                'task_id': task.task_id,
                'structure': system_structure,
                'analyzed_at': datetime.utcnow()
            })
            
            task.progress_percentage = 20.0
            
            # Extracción masiva de datos
            logger.info(f"📊 Iniciando extracción masiva de datos")
            extracted_data = await daticos_extractor.bulk_extract_database(
                limit=request.limit or 1000
            )
            
            task.progress_percentage = 60.0
            
            # Procesar y guardar datos extraídos
            logger.info(f"💾 Procesando {len(extracted_data)} registros extraídos")
            saved_count = await self._process_and_save_extracted_data(extracted_data, task.task_id)
            
            task.progress_percentage = 90.0
            
            # Análisis de calidad de datos
            quality_analysis = await daticos_extractor.analyze_data_quality(extracted_data)
            await self.db.data_quality_reports.insert_one({
                'task_id': task.task_id,
                'analysis': quality_analysis,
                'created_at': datetime.utcnow()
            })
            
            # Completar tarea
            task.status = ExtractionStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.records_extracted = saved_count
            task.progress_percentage = 100.0
            
            logger.info(f"✅ Extracción completada: {saved_count} registros guardados")
            
        except Exception as e:
            logger.error(f"❌ Error en extracción de Daticos: {e}")
            task.status = ExtractionStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            
        finally:
            await daticos_extractor.close_session()
    
    async def _process_and_save_extracted_data(self, data: List[Dict], task_id: str) -> int:
        """Procesar y guardar datos extraídos en la base de datos"""
        saved_count = 0
        
        for record in data:
            try:
                if not record.get('found') or not record.get('data'):
                    continue
                
                cedula = record.get('cedula', '')
                record_data = record['data']
                
                # Determinar si es persona física o jurídica
                is_juridica = cedula.startswith('3-') or len(cedula.split('-')) == 3
                
                # Preparar datos para inserción
                processed_record = {
                    **record_data,
                    'fuente_datos': DataSource.DATICOS_ORIGINAL.value,
                    'task_id_extraccion': task_id,
                    'extraido_en': datetime.utcnow(),
                    'actualizado_en': datetime.utcnow()
                }
                
                if is_juridica:
                    # Insertar como persona jurídica
                    processed_record['cedula_juridica'] = cedula
                    
                    # Buscar si ya existe
                    existing = await self.db.personas_juridicas.find_one(
                        {'cedula_juridica': cedula}
                    )
                    
                    if existing:
                        # Actualizar registro existente
                        await self.db.personas_juridicas.update_one(
                            {'cedula_juridica': cedula},
                            {'$set': processed_record}
                        )
                    else:
                        # Insertar nuevo registro
                        await self.db.personas_juridicas.insert_one(processed_record)
                        
                else:
                    # Insertar como persona física
                    processed_record['cedula'] = cedula
                    
                    # Buscar si ya existe
                    existing = await self.db.personas_fisicas.find_one(
                        {'cedula': cedula}
                    )
                    
                    if existing:
                        # Actualizar registro existente
                        await self.db.personas_fisicas.update_one(
                            {'cedula': cedula},
                            {'$set': processed_record}
                        )
                    else:
                        # Insertar nuevo registro  
                        await self.db.personas_fisicas.insert_one(processed_record)
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Error procesando registro {record.get('cedula', 'N/A')}: {e}")
                continue
        
        return saved_count
    
    async def get_extraction_tasks(self) -> List[AdminPanelModels.ExtractionTaskModel]:
        """Obtener lista de todas las tareas de extracción"""
        tasks = []
        
        # Tareas activas en memoria
        for task in self.active_tasks.values():
            tasks.append(AdminPanelModels.ExtractionTaskModel(
                task_id=task.task_id,
                source=task.source,
                status=task.status,
                created_at=task.created_at,
                started_at=task.started_at,
                completed_at=task.completed_at,
                records_extracted=task.records_extracted,
                total_records=task.total_records,
                error_message=task.error_message,
                progress_percentage=task.progress_percentage
            ))
        
        # Tareas históricas de la base de datos
        historical_tasks = await self.db.extraction_tasks.find().to_list(100)
        for task_doc in historical_tasks:
            if task_doc['task_id'] not in self.active_tasks:
                tasks.append(AdminPanelModels.ExtractionTaskModel(**task_doc))
        
        # Ordenar por fecha de creación (más recientes primero)
        tasks.sort(key=lambda x: x.created_at, reverse=True)
        return tasks
    
    async def cancel_extraction_task(self, task_id: str) -> bool:
        """Cancelar una tarea de extracción en curso"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            if task.status == ExtractionStatus.IN_PROGRESS:
                task.status = ExtractionStatus.CANCELLED
                task.completed_at = datetime.utcnow()
                task.error_message = "Cancelado por el administrador"
                
                # Guardar en base de datos
                await self.db.extraction_tasks.insert_one({
                    'task_id': task.task_id,
                    'source': task.source.value,
                    'status': task.status.value,
                    'created_at': task.created_at,
                    'started_at': task.started_at,
                    'completed_at': task.completed_at,
                    'records_extracted': task.records_extracted,
                    'error_message': task.error_message
                })
                
                return True
        return False
    
    async def analyze_database_quality(self) -> AdminPanelModels.DatabaseAnalysis:
        """Realizar análisis de calidad de la base de datos"""
        try:
            # Análisis de completitud por campos
            fisica_sample = await self.db.personas_fisicas.find().limit(1000).to_list(1000)
            juridica_sample = await self.db.personas_juridicas.find().limit(1000).to_list(1000)
            
            all_records = fisica_sample + juridica_sample
            total_records = len(all_records)
            
            if total_records == 0:
                return AdminPanelModels.DatabaseAnalysis(
                    data_quality_score=0.0,
                    completeness_by_field={},
                    duplicate_records=0,
                    missing_critical_fields=0,
                    geographic_coverage={},
                    temporal_distribution={}
                )
            
            # Campos importantes para análisis
            important_fields = ['nombre', 'telefono', 'provincia_id', 'canton_id', 'distrito_id']
            completeness = {}
            
            for field in important_fields:
                complete_count = sum(1 for record in all_records if record.get(field))
                completeness[field] = (complete_count / total_records) * 100
            
            # Análisis de duplicados (por cédula)
            cedulas = [r.get('cedula') or r.get('cedula_juridica') for r in all_records]
            unique_cedulas = set(filter(None, cedulas))
            duplicate_records = len(cedulas) - len(unique_cedulas)
            
            # Campos críticos faltantes
            critical_fields = ['nombre', 'cedula', 'cedula_juridica']
            missing_critical = sum(1 for record in all_records 
                                 if not any(record.get(field) for field in critical_fields))
            
            # Cobertura geográfica
            geographic_coverage = {}
            for record in all_records:
                provincia = record.get('provincia_nombre') or 'Sin provincia'
                geographic_coverage[provincia] = geographic_coverage.get(provincia, 0) + 1
            
            # Distribución temporal (por año de creación)
            temporal_distribution = {}
            current_year = datetime.utcnow().year
            for record in all_records:
                created_at = record.get('created_at')
                if created_at:
                    year = created_at.year if isinstance(created_at, datetime) else current_year
                    temporal_distribution[str(year)] = temporal_distribution.get(str(year), 0) + 1
            
            # Score de calidad general
            avg_completeness = sum(completeness.values()) / len(completeness) if completeness else 0
            duplicate_penalty = (duplicate_records / total_records) * 20 if total_records > 0 else 0
            missing_penalty = (missing_critical / total_records) * 30 if total_records > 0 else 0
            
            quality_score = max(0, avg_completeness - duplicate_penalty - missing_penalty)
            
            return AdminPanelModels.DatabaseAnalysis(
                data_quality_score=round(quality_score, 2),
                completeness_by_field=completeness,
                duplicate_records=duplicate_records,
                missing_critical_fields=missing_critical,
                geographic_coverage=geographic_coverage,
                temporal_distribution=temporal_distribution
            )
            
        except Exception as e:
            logger.error(f"Error analyzing database quality: {e}")
            raise HTTPException(status_code=500, detail=f"Error in analysis: {str(e)}")
    
    async def clean_duplicate_records(self) -> Dict[str, int]:
        """Limpiar registros duplicados de la base de datos"""
        try:
            results = {'fisica_removed': 0, 'juridica_removed': 0}
            
            # Limpiar personas físicas duplicadas
            pipeline_fisica = [
                {"$group": {
                    "_id": "$cedula",
                    "ids": {"$push": "$_id"},
                    "count": {"$sum": 1}
                }},
                {"$match": {"count": {"$gt": 1}}}
            ]
            
            fisica_duplicates = await self.db.personas_fisicas.aggregate(pipeline_fisica).to_list(1000)
            
            for duplicate in fisica_duplicates:
                # Mantener el primer registro, eliminar el resto
                ids_to_remove = duplicate['ids'][1:]
                for doc_id in ids_to_remove:
                    await self.db.personas_fisicas.delete_one({"_id": doc_id})
                    results['fisica_removed'] += 1
            
            # Limpiar personas jurídicas duplicadas
            pipeline_juridica = [
                {"$group": {
                    "_id": "$cedula_juridica",
                    "ids": {"$push": "$_id"},
                    "count": {"$sum": 1}
                }},
                {"$match": {"count": {"$gt": 1}}}
            ]
            
            juridica_duplicates = await self.db.personas_juridicas.aggregate(pipeline_juridica).to_list(1000)
            
            for duplicate in juridica_duplicates:
                # Mantener el primer registro, eliminar el resto
                ids_to_remove = duplicate['ids'][1:]
                for doc_id in ids_to_remove:
                    await self.db.personas_juridicas.delete_one({"_id": doc_id})
                    results['juridica_removed'] += 1
            
            logger.info(f"🧹 Limpieza completada: {results['fisica_removed']} físicas, {results['juridica_removed']} jurídicas eliminadas")
            return results
            
        except Exception as e:
            logger.error(f"Error cleaning duplicates: {e}")
            raise HTTPException(status_code=500, detail=f"Error cleaning duplicates: {str(e)}")

# Instancia global del gestor
admin_panel_manager = None

def get_admin_manager(db: AsyncIOMotorDatabase) -> AdminPanelManager:
    """Obtener instancia del gestor de panel de administración"""
    global admin_panel_manager
    if not admin_panel_manager:
        admin_panel_manager = AdminPanelManager(db)
    return admin_panel_manager