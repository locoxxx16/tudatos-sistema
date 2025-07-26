import asyncio
import aiohttp
import json
import logging
from typing import Optional, Dict, Any
from urllib.parse import quote
import re

logger = logging.getLogger(__name__)

class CostaRicaDataIntegrator:
    """
    Integrador de bases de datos públicas de Costa Rica
    """
    
    def __init__(self):
        self.session = None
        self.base_urls = {
            'padron_electoral': 'https://api.tse.go.cr',  # Placeholder - sujeto a disponibilidad
            'registro_nacional': 'https://api.registronacional.cr',  # Placeholder
            'neodatos': 'https://api.neodatos.com',  # API comercial disponible
        }
    
    async def get_session(self):
        """Obtener sesión HTTP asíncrona"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    async def close_session(self):
        """Cerrar sesión HTTP"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def validate_cedula(self, cedula: str) -> bool:
        """Validar formato de cédula costarricense"""
        # Remover espacios y guiones
        cedula = re.sub(r'[-\s]', '', cedula)
        
        # Cédulas físicas: 9 dígitos
        if len(cedula) == 9 and cedula.isdigit():
            return True
        
        # Cédulas jurídicas: formato 3-XXX-XXXXXX
        if len(cedula) == 10 and cedula.startswith('3'):
            return True
        
        return False
    
    async def search_padron_electoral(self, cedula: str) -> Optional[Dict[str, Any]]:
        """
        Buscar en el padrón electoral del TSE
        Nota: Esta es una implementación de ejemplo. La API real del TSE puede tener diferente estructura.
        """
        if not self.validate_cedula(cedula):
            return None
        
        try:
            session = await self.get_session()
            # Esta URL es un ejemplo - necesitaría la API real del TSE
            url = f"https://servicios.tse.go.cr/api/consulta-padron/{cedula}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'source': 'TSE_Padron_Electoral',
                        'cedula': cedula,
                        'nombre_completo': data.get('nombre_completo'),
                        'fecha_vencimiento': data.get('fecha_vencimiento'),
                        'junta_electoral': data.get('junta_electoral'),
                        'provincia': data.get('provincia'),
                        'canton': data.get('canton'),
                        'distrito': data.get('distrito')
                    }
        except Exception as e:
            logger.warning(f"Error consultando padrón electoral: {e}")
        
        return None
    
    async def search_registro_nacional_juridicas(self, cedula_juridica: str) -> Optional[Dict[str, Any]]:
        """
        Consultar registro de personas jurídicas
        """
        if not self.validate_cedula(cedula_juridica):
            return None
        
        try:
            session = await self.get_session()
            # URL de ejemplo para consulta de sociedades
            url = f"https://www.registronacional.cr/api/consulta-sociedad/{cedula_juridica}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'source': 'Registro_Nacional_Sociedades',
                        'cedula_juridica': cedula_juridica,
                        'nombre_sociedad': data.get('nombre_sociedad'),
                        'fecha_constitucion': data.get('fecha_constitucion'),
                        'estado': data.get('estado'),
                        'capital_social': data.get('capital_social'),
                        'representantes': data.get('representantes', [])
                    }
        except Exception as e:
            logger.warning(f"Error consultando registro nacional: {e}")
        
        return None
    
    async def search_neodatos_api(self, cedula: str, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Consultar API comercial Neodatos (requiere API key)
        """
        if not api_key or not self.validate_cedula(cedula):
            return None
        
        try:
            session = await self.get_session()
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            url = f"https://api.neodatos.com/v1/consulta-cedula/{cedula}"
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'source': 'Neodatos_API',
                        'cedula': cedula,
                        'datos_registro_civil': data.get('registro_civil', {}),
                        'datos_hacienda': data.get('hacienda', {}),
                        'datos_vehiculos': data.get('vehiculos', []),
                        'datos_propiedades': data.get('propiedades', []),
                        'datos_sociedades': data.get('sociedades', [])
                    }
        except Exception as e:
            logger.warning(f"Error consultando API Neodatos: {e}")
        
        return None
    
    async def enrich_persona_data(self, cedula: str, neodatos_api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Enriquecer datos de una persona consultando múltiples fuentes
        """
        results = {
            'cedula': cedula,
            'sources_consulted': [],
            'data_found': {},
            'errors': []
        }
        
        # Consultar padrón electoral
        try:
            padron_data = await self.search_padron_electoral(cedula)
            results['sources_consulted'].append('TSE_Padron_Electoral')
            if padron_data:
                results['data_found']['padron_electoral'] = padron_data
        except Exception as e:
            results['errors'].append(f"Error en padrón electoral: {str(e)}")
        
        # Si es cédula jurídica, consultar registro nacional
        if cedula.startswith('3'):
            try:
                registro_data = await self.search_registro_nacional_juridicas(cedula)
                results['sources_consulted'].append('Registro_Nacional_Sociedades')
                if registro_data:
                    results['data_found']['registro_nacional'] = registro_data
            except Exception as e:
                results['errors'].append(f"Error en registro nacional: {str(e)}")
        
        # Consultar API comercial si se proporciona key
        if neodatos_api_key:
            try:
                neodatos_data = await self.search_neodatos_api(cedula, neodatos_api_key)
                results['sources_consulted'].append('Neodatos_API')
                if neodatos_data:
                    results['data_found']['neodatos'] = neodatos_data
            except Exception as e:
                results['errors'].append(f"Error en API Neodatos: {str(e)}")
        
        return results
    
    async def search_sugef_entities(self, entity_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Consultar entidades supervisadas por SUGEF
        """
        try:
            session = await self.get_session()
            # URL de ejemplo para SUGEF
            url = "https://www.sugef.fi.cr/api/entidades-supervisadas"
            
            params = {}
            if entity_name:
                params['nombre'] = entity_name
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'source': 'SUGEF_Entidades_Supervisadas',
                        'entidades': data.get('entidades', []),
                        'total': data.get('total', 0)
                    }
        except Exception as e:
            logger.warning(f"Error consultando SUGEF: {e}")
        
        return None
    
    async def search_sicop_contracts(self, cedula_juridica: str) -> Optional[Dict[str, Any]]:
        """
        Buscar contratos públicos en SICOP por cédula jurídica
        """
        try:
            session = await self.get_session()
            # URL de ejemplo para SICOP datos abiertos
            url = "https://www.sicop.go.cr/api/datos-abiertos/contratos"
            
            params = {
                'cedula_adjudicatario': cedula_juridica,
                'formato': 'json'
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'source': 'SICOP_Contratos_Publicos',
                        'cedula_juridica': cedula_juridica,
                        'contratos': data.get('contratos', []),
                        'total_contratos': len(data.get('contratos', [])),
                        'monto_total': sum(float(c.get('monto_adjudicado', 0)) for c in data.get('contratos', []))
                    }
        except Exception as e:
            logger.warning(f"Error consultando SICOP: {e}")
        
        return None
    
    async def search_sinpe_statistics(self, entity_code: str = None) -> Optional[Dict[str, Any]]:
        """
        Consultar estadísticas de SINPE del BCCR
        """
        try:
            session = await self.get_session()
            # URL de ejemplo para estadísticas SINPE
            url = "https://www.bccr.fi.cr/api/sinpe/estadisticas"
            
            params = {}
            if entity_code:
                params['codigo_entidad'] = entity_code
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'source': 'BCCR_SINPE_Estadisticas',
                        'estadisticas': data.get('estadisticas', {}),
                        'periodo': data.get('periodo'),
                        'entidad': entity_code
                    }
        except Exception as e:
            logger.warning(f"Error consultando SINPE: {e}")
        
        return None
    
    async def search_hacienda_tributarios(self, cedula: str) -> Optional[Dict[str, Any]]:
        """
        Consultar información tributaria del Ministerio de Hacienda
        """
        try:
            session = await self.get_session()
            # URL de ejemplo para datos tributarios
            url = f"https://www.hacienda.go.cr/api/tributarios/{cedula}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'source': 'Ministerio_Hacienda_Tributarios',
                        'cedula': cedula,
                        'estado_tributario': data.get('estado'),
                        'regimen_fiscal': data.get('regimen'),
                        'actividades_economicas': data.get('actividades', [])
                    }
        except Exception as e:
            logger.warning(f"Error consultando Hacienda: {e}")
        
        return None
    
    async def search_sfe_organicos(self, empresa: str = None) -> Optional[Dict[str, Any]]:
        """
        Consultar certificaciones orgánicas del SFE
        """
        try:
            session = await self.get_session()
            # URL de ejemplo para datos del SFE
            url = "https://www.sfe.go.cr/api/certificaciones-organicas"
            
            params = {}
            if empresa:
                params['empresa'] = empresa
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'source': 'SFE_Certificaciones_Organicas',
                        'certificaciones': data.get('certificaciones', []),
                        'areas_certificadas': data.get('areas_certificadas', 0)
                    }
        except Exception as e:
            logger.warning(f"Error consultando SFE: {e}")
        
        return None
    
    async def comprehensive_business_lookup(self, cedula_juridica: str) -> Dict[str, Any]:
        """
        Búsqueda comprehensiva de una empresa en múltiples fuentes gubernamentales
        """
        results = {
            'cedula_juridica': cedula_juridica,
            'sources_consulted': [],
            'data_found': {},
            'errors': []
        }
        
        # SUGEF - Entidades financieras supervisadas
        try:
            sugef_data = await self.search_sugef_entities(cedula_juridica)
            results['sources_consulted'].append('SUGEF')
            if sugef_data:
                results['data_found']['sugef'] = sugef_data
        except Exception as e:
            results['errors'].append(f"Error en SUGEF: {str(e)}")
        
        # SICOP - Contratos públicos
        try:
            sicop_data = await self.search_sicop_contracts(cedula_juridica)
            results['sources_consulted'].append('SICOP')
            if sicop_data:
                results['data_found']['sicop'] = sicop_data
        except Exception as e:
            results['errors'].append(f"Error en SICOP: {str(e)}")
        
        # Hacienda - Información tributaria
        try:
            hacienda_data = await self.search_hacienda_tributarios(cedula_juridica)
            results['sources_consulted'].append('Hacienda')
            if hacienda_data:
                results['data_found']['hacienda'] = hacienda_data
        except Exception as e:
            results['errors'].append(f"Error en Hacienda: {str(e)}")
        
        # SFE - Certificaciones orgánicas
        try:
            sfe_data = await self.search_sfe_organicos()
            results['sources_consulted'].append('SFE')
            if sfe_data:
                results['data_found']['sfe'] = sfe_data
        except Exception as e:
            results['errors'].append(f"Error en SFE: {str(e)}")
        
        return results

# Funciones de utilidad para limpieza y validación de datos
class DataCleaner:
    
    @staticmethod
    def clean_phone_number(phone: str) -> str:
        """Limpiar y formatear números telefónicos"""
        if not phone:
            return ""
        
        # Remover caracteres no numéricos excepto +
        phone = re.sub(r'[^\d+]', '', phone)
        
        # Agregar código de país si no está presente
        if not phone.startswith('+'):
            if phone.startswith('506'):
                phone = '+' + phone
            elif len(phone) == 8:  # Número local de CR
                phone = '+506' + phone
        
        return phone
    
    @staticmethod  
    def standardize_address(address: str, provincia: str, canton: str, distrito: str) -> str:
        """Estandarizar formato de direcciones"""
        if not address:
            return f"{distrito}, {canton}, {provincia}"
        
        # Limpiar dirección
        address = address.strip()
        
        # Agregar ubicación si no está incluida
        if provincia.lower() not in address.lower():
            address = f"{address}, {distrito}, {canton}, {provincia}"
        
        return address
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validar formato de email"""
        if not email:
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))

# Instancia global del integrador
costa_rica_integrator = CostaRicaDataIntegrator()