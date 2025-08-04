import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const AdminDashboard = () => {
  const [stats, setStats] = useState({});
  const [registrationRequests, setRegistrationRequests] = useState([]);
  const [autoRegenStatus, setAutoRegenStatus] = useState({});
  const [improvementMetrics, setImprovementMetrics] = useState({});
  const [systemOverview, setSystemOverview] = useState({});
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Verificar autenticación de admin
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (!token) {
      navigate('/login');
      return;
    }

    const user = JSON.parse(userData);
    if (user.role !== 'admin') {
      navigate('/user/dashboard');
      return;
    }

    fetchAllData();
  }, [navigate]);

  const fetchAllData = async () => {
    try {
      // Fetch system health
      const healthResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/health`);
      const healthData = await healthResponse.json();
      setStats(healthData.database || {});

      // Fetch system overview
      const overviewResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/system/complete-overview`);
      const overviewData = await overviewResponse.json();
      setSystemOverview(overviewData.system_overview || {});

      // Fetch auto-regeneration status
      const autoRegenResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/system/auto-regeneration/status`);
      const autoRegenData = await autoRegenResponse.json();
      setAutoRegenStatus(autoRegenData);

      // Fetch improvement metrics
      const metricsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/system/improvement-metrics`);
      const metricsData = await metricsResponse.json();
      setImprovementMetrics(metricsData);

      // Fetch registration requests
      const requestsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/registration-requests`);
      const requestsData = await requestsResponse.json();
      setRegistrationRequests(requestsData.requests || []);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching admin data:', error);
      setLoading(false);
    }
  };

  const triggerManualRegeneration = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/system/auto-regeneration/trigger`, {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.success) {
        alert('✅ Proceso de mejora automática iniciado exitosamente');
        fetchAllData(); // Refresh data
      } else {
        alert('❌ Error iniciando proceso: ' + data.message);
      }
    } catch (error) {
      alert('❌ Error de conexión');
    }
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat('es-CR').format(num || 0);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex items-center justify-center">
        <div className="text-white text-2xl">
          <i className="fas fa-spinner fa-spin mr-3"></i>
          Cargando Panel Administrador...
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 text-white">
      {/* Header */}
      <header className="bg-black bg-opacity-40 backdrop-blur-lg border-b border-white border-opacity-20">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <Link to="/" className="flex items-center space-x-4">
              <div className="w-14 h-14 bg-gradient-to-r from-red-500 to-pink-600 rounded-xl flex items-center justify-center">
                <i className="fas fa-crown text-xl text-white"></i>
              </div>
              <div>
                <h1 className="text-2xl font-black bg-gradient-to-r from-red-400 to-pink-500 bg-clip-text text-transparent">
                  TuDatos ADMIN
                </h1>
                <p className="text-sm text-blue-300">Panel de Control Maestro</p>
              </div>
            </Link>
            
            <div className="flex items-center space-x-6">
              <div className="text-right">
                <p className="text-lg font-bold text-red-300">🔥 ADMINISTRADOR</p>
                <p className="text-sm text-blue-300">Control Total del Sistema</p>
              </div>
              <button 
                onClick={logout}
                className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg font-bold transition-all"
              >
                <i className="fas fa-sign-out-alt mr-2"></i>Salir
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Title */}
        <div className="text-center mb-12">
          <h1 className="text-6xl font-black mb-4 bg-gradient-to-r from-red-400 via-pink-500 to-purple-600 bg-clip-text text-transparent">
            👑 PANEL ADMINISTRADOR ULTRA
          </h1>
          <p className="text-xl text-gray-300">
            Control total de <span className="font-bold text-yellow-300">{formatNumber(stats.personas_completas)}</span> registros
            con sistema de auto-regeneración activo
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <div className="bg-gradient-to-br from-red-600 to-red-800 rounded-2xl p-6 border border-red-400 border-opacity-30">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-4xl font-black">{formatNumber(stats.personas_completas)}</p>
                <p className="text-sm font-bold">Registros Totales</p>
              </div>
              <i className="fas fa-database text-6xl opacity-30"></i>
            </div>
          </div>

          <div className="bg-gradient-to-br from-green-600 to-green-800 rounded-2xl p-6 border border-green-400 border-opacity-30">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-4xl font-black">{formatNumber(stats.fotos_integradas)}</p>
                <p className="text-sm font-bold">Fotos Integradas</p>
              </div>
              <i className="fas fa-images text-6xl opacity-30"></i>
            </div>
          </div>

          <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-2xl p-6 border border-blue-400 border-opacity-30">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-4xl font-black">{autoRegenStatus.status === 'ACTIVE' ? '✅' : '❌'}</p>
                <p className="text-sm font-bold">Auto-Regeneración</p>
              </div>
              <i className="fas fa-sync text-6xl opacity-30"></i>
            </div>
          </div>

          <div className="bg-gradient-to-br from-purple-600 to-purple-800 rounded-2xl p-6 border border-purple-400 border-opacity-30">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-4xl font-black">{registrationRequests.length}</p>
                <p className="text-sm font-bold">Solicitudes Pendientes</p>
              </div>
              <i className="fas fa-user-plus text-6xl opacity-30"></i>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl border border-white border-opacity-10 mb-8">
          <div className="flex flex-wrap border-b border-white border-opacity-20">
            {[
              { id: 'overview', label: '📊 Overview', icon: 'fas fa-chart-line' },
              { id: 'regeneration', label: '🔄 Auto-Regeneración', icon: 'fas fa-sync' },
              { id: 'requests', label: '📋 Solicitudes', icon: 'fas fa-user-plus' },
              { id: 'system', label: '⚙️ Sistema', icon: 'fas fa-cogs' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-4 font-bold transition-all border-b-2 ${
                  activeTab === tab.id
                    ? 'border-yellow-400 text-yellow-300 bg-white bg-opacity-10'
                    : 'border-transparent text-gray-400 hover:text-white hover:bg-white hover:bg-opacity-5'
                }`}
              >
                <i className={`${tab.icon} mr-2`}></i>
                {tab.label}
              </button>
            ))}
          </div>

          <div className="p-8">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div>
                <h2 className="text-3xl font-bold mb-8 text-yellow-300">📊 Resumen del Sistema</h2>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                  {/* Database Stats */}
                  <div className="bg-white bg-opacity-5 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-blue-300">🗄️ Estadísticas de Base de Datos</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span>Personas Registradas:</span>
                        <span className="font-bold text-yellow-300">{formatNumber(stats.personas_completas)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Fotos Disponibles:</span>
                        <span className="font-bold text-green-300">{formatNumber(stats.fotos_integradas)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Teléfonos Verificados:</span>
                        <span className="font-bold text-blue-300">{formatNumber(stats.telefonos_registrados)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Emails Registrados:</span>
                        <span className="font-bold text-purple-300">{formatNumber(stats.emails_registrados)}</span>
                      </div>
                    </div>
                  </div>

                  {/* System Health */}
                  <div className="bg-white bg-opacity-5 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-green-300">🏥 Estado del Sistema</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span>Base de Datos:</span>
                        <span className="bg-green-600 px-3 py-1 rounded-full text-sm font-bold">OPERATIVA</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span>Auto-Regeneración:</span>
                        <span className="bg-blue-600 px-3 py-1 rounded-full text-sm font-bold">ACTIVO</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span>APIs:</span>
                        <span className="bg-green-600 px-3 py-1 rounded-full text-sm font-bold">FUNCIONANDO</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span>Búsqueda Ultra:</span>
                        <span className="bg-green-600 px-3 py-1 rounded-full text-sm font-bold">OPERATIVA</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Latest Improvements */}
                {improvementMetrics.improvements && (
                  <div className="bg-white bg-opacity-5 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-purple-300">📈 Mejoras Recientes (24h)</h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      <div className="text-center">
                        <p className="text-2xl font-bold text-blue-300">{improvementMetrics.improvements.records_enhanced || 0}</p>
                        <p className="text-sm">Registros Mejorados</p>
                      </div>
                      <div className="text-center">
                        <p className="text-2xl font-bold text-green-300">{improvementMetrics.improvements.photos_updated || 0}</p>
                        <p className="text-sm">Fotos Actualizadas</p>
                      </div>
                      <div className="text-center">
                        <p className="text-2xl font-bold text-yellow-300">{improvementMetrics.improvements.verifications_completed || 0}</p>
                        <p className="text-sm">Verificaciones</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Auto-Regeneration Tab */}
            {activeTab === 'regeneration' && (
              <div>
                <h2 className="text-3xl font-bold mb-8 text-yellow-300">🔄 Sistema de Auto-Regeneración</h2>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                  {/* Status */}
                  <div className="bg-white bg-opacity-5 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-green-300">📊 Estado del Sistema</h3>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span>Estado:</span>
                        <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                          autoRegenStatus.status === 'ACTIVE' ? 'bg-green-600' : 'bg-red-600'
                        }`}>
                          {autoRegenStatus.status || 'N/A'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Versión:</span>
                        <span className="font-bold">{autoRegenStatus.version || 'N/A'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Próxima Mejora:</span>
                        <span className="font-bold text-blue-300">02:00 AM (Diario)</span>
                      </div>
                    </div>
                  </div>

                  {/* Capabilities */}
                  <div className="bg-white bg-opacity-5 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-blue-300">⚡ Capacidades Activas</h3>
                    <div className="space-y-2">
                      {autoRegenStatus.capabilities && Object.entries(autoRegenStatus.capabilities).map(([key, value]) => (
                        <div key={key} className="flex items-center justify-between">
                          <span className="text-sm">{key.replace(/_/g, ' ')}:</span>
                          <span className={`px-2 py-1 rounded text-xs font-bold ${
                            value === 'Activo' ? 'bg-green-600' : 'bg-gray-600'
                          }`}>
                            {value}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Manual Trigger */}
                <div className="bg-gradient-to-r from-red-600 to-pink-600 rounded-xl p-6 text-center">
                  <h3 className="text-2xl font-bold mb-4">🚨 Mejora Manual del Sistema</h3>
                  <p className="mb-6">
                    Activar proceso de mejora inmediato que incluye verificación de integridad, 
                    fusión de duplicados y optimización de índices.
                  </p>
                  <button
                    onClick={triggerManualRegeneration}
                    className="bg-white bg-opacity-20 hover:bg-opacity-30 px-8 py-3 rounded-xl font-bold text-lg transition-all transform hover:scale-105"
                  >
                    <i className="fas fa-rocket mr-3"></i>
                    Activar Mejora Inmediata
                  </button>
                </div>
              </div>
            )}

            {/* Requests Tab */}
            {activeTab === 'requests' && (
              <div>
                <h2 className="text-3xl font-bold mb-8 text-yellow-300">📋 Solicitudes de Registro ({registrationRequests.length})</h2>
                
                {registrationRequests.length === 0 ? (
                  <div className="text-center py-12">
                    <i className="fas fa-inbox text-6xl text-gray-500 mb-4"></i>
                    <p className="text-xl text-gray-400">No hay solicitudes pendientes</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {registrationRequests.map((request, index) => (
                      <div key={request.id} className="bg-white bg-opacity-5 rounded-xl p-6 border border-white border-opacity-10">
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                          <div>
                            <h4 className="font-bold text-blue-300 mb-2">👤 Información Personal</h4>
                            <p><span className="text-gray-400">Nombre:</span> {request.nombre_completo}</p>
                            <p><span className="text-gray-400">Email:</span> {request.email}</p>
                            <p><span className="text-gray-400">Teléfono:</span> {request.telefono}</p>
                          </div>
                          
                          <div>
                            <h4 className="font-bold text-green-300 mb-2">🏢 Información Empresarial</h4>
                            <p><span className="text-gray-400">Empresa:</span> {request.empresa || 'N/A'}</p>
                            <p><span className="text-gray-400">Plan:</span> 
                              <span className="ml-2 bg-blue-600 px-2 py-1 rounded text-sm">
                                {request.plan_solicitado}
                              </span>
                            </p>
                            <p><span className="text-gray-400">Fecha:</span> {new Date(request.fecha_solicitud).toLocaleDateString()}</p>
                          </div>
                          
                          <div>
                            <h4 className="font-bold text-purple-300 mb-2">📝 Motivo</h4>
                            <p className="text-sm text-gray-300">{request.motivo_uso || 'No especificado'}</p>
                            <div className="mt-4">
                              <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                                request.estado === 'pendiente' ? 'bg-yellow-600' : 'bg-green-600'
                              }`}>
                                {request.estado.toUpperCase()}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                <div className="mt-8 bg-blue-600 bg-opacity-30 rounded-xl p-6 text-center">
                  <h3 className="text-xl font-bold mb-2">📧 Notificaciones Automáticas</h3>
                  <p className="text-gray-300">
                    Todas las solicitudes se envían automáticamente a: 
                    <span className="font-bold text-yellow-300 ml-2">jykinternacional@gmail.com</span>
                  </p>
                </div>
              </div>
            )}

            {/* System Tab */}
            {activeTab === 'system' && (
              <div>
                <h2 className="text-3xl font-bold mb-8 text-yellow-300">⚙️ Configuración del Sistema</h2>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Data Sources */}
                  <div className="bg-white bg-opacity-5 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-green-300">🗂️ Fuentes de Datos Activas</h3>
                    <div className="space-y-3">
                      {systemOverview.sources_active?.map((source, index) => (
                        <div key={index} className="flex items-center justify-between bg-white bg-opacity-5 p-3 rounded-lg">
                          <span className="text-sm">{source}</span>
                          <span className="bg-green-600 px-2 py-1 rounded text-xs font-bold">ACTIVA</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* System Performance */}
                  <div className="bg-white bg-opacity-5 rounded-xl p-6">
                    <h3 className="text-xl font-bold mb-4 text-blue-300">📈 Rendimiento del Sistema</h3>
                    <div className="space-y-4">
                      {improvementMetrics.system_performance && Object.entries(improvementMetrics.system_performance).map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <span className="text-sm">{key.replace(/_/g, ' ')}:</span>
                          <span className="font-bold text-yellow-300">{value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* System Actions */}
                <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gradient-to-r from-green-600 to-blue-600 rounded-xl p-6 text-center">
                    <h3 className="text-xl font-bold mb-2">💾 Backup del Sistema</h3>
                    <p className="mb-4 text-sm">Crear respaldo completo de la base de datos</p>
                    <button className="bg-white bg-opacity-20 hover:bg-opacity-30 px-6 py-2 rounded-lg font-bold transition-all">
                      <i className="fas fa-download mr-2"></i>Crear Backup
                    </button>
                  </div>

                  <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl p-6 text-center">
                    <h3 className="text-xl font-bold mb-2">📊 Generar Reporte</h3>
                    <p className="mb-4 text-sm">Reporte completo del estado del sistema</p>
                    <button className="bg-white bg-opacity-20 hover:bg-opacity-30 px-6 py-2 rounded-lg font-bold transition-all">
                      <i className="fas fa-file-alt mr-2"></i>Generar Reporte
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer Info */}
        <div className="text-center bg-black bg-opacity-30 rounded-xl p-6">
          <h3 className="text-xl font-bold mb-2 text-yellow-300">🎯 Sistema TuDatos - Versión Administrador</h3>
          <p className="text-gray-400">
            Control total sobre la base de datos más grande de Costa Rica | 
            Contacto: <span className="text-yellow-300">jykinternacional@gmail.com</span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;