import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const UserDashboard = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({});
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Verificar autenticación
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (!token) {
      navigate('/login');
      return;
    }

    setUser(JSON.parse(userData));
    fetchSystemStats();
  }, [navigate]);

  const fetchSystemStats = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/health`);
      const data = await response.json();
      setStats(data.database || {});
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!searchQuery.trim()) {
      alert('⚠️ Por favor ingrese un término de búsqueda');
      return;
    }

    setLoading(true);
    setSearchResults([]);

    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/search/ultra-complete?query=${encodeURIComponent(searchQuery)}`
      );
      const data = await response.json();

      if (data.success) {
        setSearchResults(data.profiles || []);
      } else {
        alert('❌ ' + data.message);
      }
    } catch (error) {
      alert('❌ Error en la búsqueda');
    } finally {
      setLoading(false);
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

  if (!user) {
    return <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="text-white text-xl">Cargando...</div>
    </div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 text-white">
      {/* Header */}
      <header className="bg-black bg-opacity-30 backdrop-blur-lg border-b border-white border-opacity-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <Link to="/" className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-xl flex items-center justify-center">
                <i className="fas fa-database text-xl text-white"></i>
              </div>
              <div>
                <h1 className="text-2xl font-black bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
                  TuDatos
                </h1>
                <p className="text-sm text-blue-300">Panel Usuario</p>
              </div>
            </Link>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-lg font-bold">{user.username}</p>
                <p className="text-sm text-blue-300">Usuario Activo</p>
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
        {/* Welcome Section */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-black mb-4 bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
            🎯 Panel de Búsqueda Ultra Completa
          </h1>
          <p className="text-xl text-gray-300">
            Acceso a <span className="font-bold text-yellow-300">{formatNumber(stats.personas_completas)}</span> registros
            con fotos, WhatsApp, análisis crediticio y fusión inteligente
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-6 border border-white border-opacity-10">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-4xl font-black text-yellow-300">{formatNumber(stats.personas_completas)}</p>
                <p className="text-sm font-bold">Registros Totales</p>
              </div>
              <i className="fas fa-users text-5xl text-yellow-400 opacity-50"></i>
            </div>
          </div>

          <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-6 border border-white border-opacity-10">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-4xl font-black text-green-300">{formatNumber(stats.fotos_integradas)}</p>
                <p className="text-sm font-bold">Fotos Disponibles</p>
              </div>
              <i className="fas fa-camera text-5xl text-green-400 opacity-50"></i>
            </div>
          </div>

          <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-6 border border-white border-opacity-10">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-4xl font-black text-blue-300">{formatNumber(stats.telefonos_registrados)}</p>
                <p className="text-sm font-bold">Teléfonos</p>
              </div>
              <i className="fab fa-whatsapp text-5xl text-blue-400 opacity-50"></i>
            </div>
          </div>

          <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-6 border border-white border-opacity-10">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-4xl font-black text-purple-300">{formatNumber(stats.emails_registrados)}</p>
                <p className="text-sm font-bold">Emails</p>
              </div>
              <i className="fas fa-envelope text-5xl text-purple-400 opacity-50"></i>
            </div>
          </div>
        </div>

        {/* Search Section */}
        <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl p-8 border border-white border-opacity-10 mb-8">
          <h2 className="text-3xl font-bold mb-6 text-center text-yellow-300">
            🔍 Búsqueda Ultra Completa
          </h2>
          
          <form onSubmit={handleSearch} className="mb-8">
            <div className="flex gap-4">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 px-6 py-4 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-xl text-white placeholder-gray-400 text-lg focus:outline-none focus:ring-2 focus:ring-yellow-400"
                placeholder="Buscar por nombre, cédula, email o teléfono..."
              />
              <button
                type="submit"
                disabled={loading}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 px-8 py-4 rounded-xl font-bold text-lg transition-all disabled:opacity-50 transform hover:scale-105"
              >
                <i className={`mr-3 ${loading ? 'fas fa-spinner fa-spin' : 'fas fa-search'}`}></i>
                {loading ? 'Buscando...' : 'Buscar'}
              </button>
            </div>
          </form>

          <div className="text-center text-sm text-gray-400">
            <p>
              <i className="fas fa-info-circle mr-2"></i>
              Búsqueda inteligente con fusión de datos, verificación WhatsApp y análisis crediticio automático
            </p>
          </div>
        </div>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className="space-y-6">
            <h3 className="text-2xl font-bold text-yellow-300">
              📊 Resultados de Búsqueda ({searchResults.length})
            </h3>
            
            {searchResults.map((profile, index) => (
              <div key={index} className="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-6 border border-white border-opacity-10">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Información Básica */}
                  <div>
                    <h4 className="text-xl font-bold text-yellow-300 mb-4">👤 Información Personal</h4>
                    <div className="space-y-2">
                      <p><span className="font-bold text-blue-300">Cédula:</span> {profile.cedula}</p>
                      <p><span className="font-bold text-blue-300">Nombre:</span> {profile.nombres?.nombre_completo || 'N/A'}</p>
                      <p><span className="font-bold text-blue-300">Fuentes:</span> {profile.fuentes_verificacion?.join(', ')}</p>
                      <p><span className="font-bold text-blue-300">Completitud:</span> 
                        <span className="ml-2 bg-green-600 px-2 py-1 rounded text-sm">
                          {profile.metadata?.profile_completeness}%
                        </span>
                      </p>
                    </div>
                  </div>

                  {/* Información de Contacto */}
                  <div>
                    <h4 className="text-xl font-bold text-green-300 mb-4">📱 Contacto</h4>
                    <div className="space-y-2">
                      {profile.contacto?.emails?.map((email, i) => (
                        <p key={i}>
                          <span className="font-bold text-blue-300">Email:</span> {email.email}
                          {email.verified && <i className="fas fa-check-circle text-green-400 ml-2"></i>}
                        </p>
                      ))}
                      {profile.contacto?.telefonos?.map((tel, i) => (
                        <p key={i}>
                          <span className="font-bold text-blue-300">Teléfono:</span> {tel.numero}
                          {tel.whatsapp?.has_whatsapp && (
                            <span className="ml-2 bg-green-600 px-2 py-1 rounded text-xs">
                              <i className="fab fa-whatsapp mr-1"></i>WhatsApp
                            </span>
                          )}
                        </p>
                      ))}
                    </div>
                  </div>

                  {/* Análisis Crediticio */}
                  {profile.credito && (
                    <div>
                      <h4 className="text-xl font-bold text-red-300 mb-4">💳 Análisis Crediticio</h4>
                      <div className="space-y-2">
                        <p><span className="font-bold text-blue-300">Score:</span> {profile.credito.score_crediticio}</p>
                        <p><span className="font-bold text-blue-300">Clasificación:</span> {profile.credito.clasificacion}</p>
                        <p><span className="font-bold text-blue-300">Capacidad:</span> {profile.credito.capacidad_pago}</p>
                      </div>
                    </div>
                  )}

                  {/* Propiedades */}
                  {profile.propiedades && (
                    <div>
                      <h4 className="text-xl font-bold text-purple-300 mb-4">🏠 Propiedades & Vehículos</h4>
                      <div className="space-y-2">
                        {profile.propiedades.vehiculos?.map((vehiculo, i) => (
                          <p key={i} className="text-sm">
                            <span className="font-bold text-blue-300">Vehículo:</span> 
                            {vehiculo.marca} {vehiculo.modelo} ({vehiculo.año})
                            <br/>
                            <span className="text-xs text-gray-300">
                              Placa: {vehiculo.placa} | Valor: ₡{vehiculo.valor_estimado?.toLocaleString()}
                            </span>
                          </p>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Redes Sociales */}
                {profile.redes_sociales && (
                  <div className="mt-6 pt-6 border-t border-white border-opacity-20">
                    <h4 className="text-lg font-bold text-pink-300 mb-3">🌐 Redes Sociales</h4>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(profile.redes_sociales).map(([platform, data]) => (
                        data.found && (
                          <span key={platform} className="bg-blue-600 px-3 py-1 rounded-full text-sm">
                            <i className={`fab fa-${platform} mr-1`}></i>
                            {platform.charAt(0).toUpperCase() + platform.slice(1)}
                          </span>
                        )
                      ))}
                    </div>
                  </div>
                )}

                {/* Confiabilidad */}
                <div className="mt-4 text-center">
                  <span className="bg-gradient-to-r from-green-600 to-blue-600 px-4 py-2 rounded-full text-sm font-bold">
                    <i className="fas fa-shield-check mr-2"></i>
                    Confiabilidad: {profile.confiabilidad?.nivel} ({profile.confiabilidad?.score}/100)
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Features Info */}
        <div className="mt-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-center">
          <h3 className="text-2xl font-bold mb-4">🚀 Capacidades Ultra Completas</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <i className="fas fa-brain text-2xl mb-2 text-yellow-300"></i>
              <p className="font-bold">Fusión Inteligente</p>
            </div>
            <div>
              <i className="fab fa-whatsapp text-2xl mb-2 text-green-300"></i>
              <p className="font-bold">WhatsApp Verificado</p>
            </div>
            <div>
              <i className="fas fa-chart-line text-2xl mb-2 text-blue-300"></i>
              <p className="font-bold">Análisis Crediticio</p>
            </div>
            <div>
              <i className="fas fa-home text-2xl mb-2 text-purple-300"></i>
              <p className="font-bold">Propiedades & Bienes</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserDashboard;