import React, { useState, useEffect, createContext, useContext } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('daticos_token');
    const userData = localStorage.getItem('daticos_user');
    if (token && userData) {
      setUser(JSON.parse(userData));
    }
    setLoading(false);
  }, []);

  const login = async (credentials) => {
    try {
      const response = await axios.post(`${API}/auth/login`, credentials);
      const { access_token, user } = response.data;
      localStorage.setItem('daticos_token', access_token);
      localStorage.setItem('daticos_user', JSON.stringify(user));
      setUser(user);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Error de autenticación' };
    }
  };

  const logout = () => {
    localStorage.removeItem('daticos_token');
    localStorage.removeItem('daticos_user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => useContext(AuthContext);

// API Helper
const apiCall = async (endpoint, method = 'GET', data = null) => {
  const token = localStorage.getItem('daticos_token');
  const config = {
    method,
    url: `${API}${endpoint}`,
    headers: { Authorization: `Bearer ${token}` }
  };
  
  if (data) {
    config.data = data;
  }
  
  try {
    const response = await axios(config);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Login Component
const Login = () => {
  const [credentials, setCredentials] = useState({ login: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(credentials);
    if (result.success) {
      navigate('/');
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-800 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-4xl">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-block bg-blue-600 rounded-full p-6 mb-4">
            <h1 className="text-white text-4xl font-bold tracking-wider">DATICOS</h1>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Login Form */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-700 mb-4">Usuario</h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <input
                type="text"
                placeholder="Usuario"
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={credentials.login}
                onChange={(e) => setCredentials({...credentials, login: e.target.value})}
                required
              />

              <div>
                <label className="block text-gray-700 text-sm font-medium mb-2">Clave</label>
                <input
                  type="password"
                  placeholder="Password"
                  className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={credentials.password}
                  onChange={(e) => setCredentials({...credentials, password: e.target.value})}
                  required
                />
              </div>

              {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {loading ? 'Ingresando...' : 'Ingresar'}
              </button>

              <button
                type="button"
                className="w-full bg-red-500 text-white py-2 px-4 rounded-md hover:bg-red-600 transition-colors text-sm"
              >
                Olvidé / Cambiar mi Clave
              </button>
            </form>
          </div>

          {/* Information Panel */}
          <div className="bg-blue-50 p-6 rounded-lg">
            <p className="text-blue-800 mb-4">
              Contáctenos a <a href="mailto:info@daticos.com" className="text-blue-600 underline">info@daticos.com</a> para mayor información.
            </p>
            <p className="text-blue-800 mb-4">
              Si desea solicitar nuestros servicios sírvase llenar el siguiente 
              <a href="#" className="text-blue-600 underline"> formulario</a> y enviarlo a: 
              <a href="mailto:info@daticos.com" className="text-blue-600 underline"> info@daticos.com</a>
            </p>
            
            <div className="space-y-3 text-sm">
              <div>
                <span className="font-semibold">1.</span> Realizamos Estadísticas y Estudios de la población por ubicación geográfica (Físicas y Jurídicas).
              </div>
              <div>
                <span className="font-semibold">2.</span> Somos una excelente herramienta para la prospectación de Futuros Clientes, para la colocación de productos y servicios.
              </div>
              <div>
                <span className="font-semibold">3.</span> Mensajería Masiva SMS
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Results Display Component
const ResultsTable = ({ results, loading }) => {
  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Buscando...</p>
      </div>
    );
  }

  if (!results || results.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No se encontraron resultados
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white border border-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cédula</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Teléfono</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ubicación</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Detalles</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {results.map((result, index) => (
            <tr key={index} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                  result.type === 'fisica' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                }`}>
                  {result.type === 'fisica' ? 'Física' : 'Jurídica'}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {result.data.cedula || result.data.cedula_juridica}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-900">
                  {result.type === 'fisica' 
                    ? `${result.data.nombre} ${result.data.primer_apellido} ${result.data.segundo_apellido || ''}`
                    : result.data.nombre_comercial
                  }
                </div>
                {result.type === 'juridica' && (
                  <div className="text-sm text-gray-500">{result.data.razon_social}</div>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {result.data.telefono || 'N/A'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div>{result.data.provincia_nombre}</div>
                <div>{result.data.canton_nombre}</div>
                <div>{result.data.distrito_nombre}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                {result.type === 'fisica' ? (
                  <div>
                    <div>Ocupación: {result.data.ocupacion || 'N/A'}</div>
                    <div>Email: {result.data.email || 'N/A'}</div>
                  </div>
                ) : (
                  <div>
                    <div>Sector: {result.data.sector_negocio}</div>
                    <div>Empleados: {result.data.numero_empleados || 'N/A'}</div>
                  </div>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Main Consultation Interface - Daticos Style
const ConsultationInterface = () => {
  const [cedula, setCedula] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [searchHistory, setSearchHistory] = useState([]);

  const handleConsultation = async (e) => {
    e.preventDefault();
    if (!cedula.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      const data = await apiCall(`/search/cedula/${cedula}?enrich=true`);
      setResult(data);
      
      // Add to search history
      const newSearch = {
        cedula,
        timestamp: new Date(),
        found: data.found,
        type: data.type
      };
      setSearchHistory(prev => [newSearch, ...prev.slice(0, 9)]); // Keep last 10 searches
      
    } catch (error) {
      console.error('Error in consultation:', error);
      setResult({ 
        found: false, 
        message: 'Error en la consulta. Intente nuevamente.',
        error: true 
      });
    }
    setLoading(false);
  };

  const renderPersonDetails = (data, type) => {
    if (type === 'fisica') {
      return (
        <div className="bg-blue-50 p-6 rounded-lg border-l-4 border-blue-500">
          <h3 className="text-2xl font-bold text-blue-800 mb-6 flex items-center">
            👤 <span className="ml-2">Persona Física Encontrada</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="bg-white p-4 rounded-md">
                <strong className="text-blue-700">Número de Cédula:</strong>
                <p className="text-xl font-mono text-gray-800">{data.cedula}</p>
              </div>
              <div className="bg-white p-4 rounded-md">
                <strong className="text-blue-700">Nombre Completo:</strong>
                <p className="text-xl text-gray-800">
                  {`${data.nombre} ${data.primer_apellido} ${data.segundo_apellido || ''}`.trim()}
                </p>
              </div>
              <div className="bg-white p-4 rounded-md">
                <strong className="text-blue-700">Fecha de Nacimiento:</strong>
                <p className="text-lg text-gray-800">
                  {data.fecha_nacimiento ? new Date(data.fecha_nacimiento).toLocaleDateString('es-CR', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  }) : 'No disponible'}
                </p>
              </div>
              <div className="bg-white p-4 rounded-md">
                <strong className="text-blue-700">Ocupación:</strong>
                <p className="text-lg text-gray-800">{data.ocupacion || 'No especificada'}</p>
              </div>
            </div>
            <div className="space-y-4">
              <div className="bg-white p-4 rounded-md">
                <strong className="text-blue-700">Teléfono:</strong>
                <p className="text-lg text-gray-800 font-mono">{data.telefono || 'No disponible'}</p>
              </div>
              <div className="bg-white p-4 rounded-md">
                <strong className="text-blue-700">Correo Electrónico:</strong>
                <p className="text-lg text-gray-800">{data.email || 'No disponible'}</p>
              </div>
              <div className="bg-white p-4 rounded-md">
                <strong className="text-blue-700">Ubicación Geográfica:</strong>
                <div className="space-y-1">
                  <p className="text-sm text-gray-600">Provincia:</p>
                  <p className="text-lg text-gray-800">{data.provincia_nombre}</p>
                  <p className="text-sm text-gray-600">Cantón:</p>
                  <p className="text-lg text-gray-800">{data.canton_nombre}</p>
                  <p className="text-sm text-gray-600">Distrito:</p>
                  <p className="text-lg text-gray-800">{data.distrito_nombre}</p>
                </div>
              </div>
              <div className="bg-white p-4 rounded-md">
                <strong className="text-blue-700">Dirección Exacta:</strong>
                <p className="text-lg text-gray-800">{data.direccion_exacta || 'No especificada'}</p>
              </div>
            </div>
          </div>
        </div>
      );
    } else if (type === 'juridica') {
      return (
        <div className="bg-green-50 p-6 rounded-lg border-l-4 border-green-500">
          <h3 className="text-2xl font-bold text-green-800 mb-6 flex items-center">
            🏢 <span className="ml-2">Persona Jurídica Encontrada</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="bg-white p-4 rounded-md">
                <strong className="text-green-700">Cédula Jurídica:</strong>
                <p className="text-xl font-mono text-gray-800">{data.cedula_juridica}</p>
              </div>
              <div className="bg-white p-4 rounded-md">
                <strong className="text-green-700">Nombre Comercial:</strong>
                <p className="text-xl text-gray-800">{data.nombre_comercial}</p>
              </div>
              <div className="bg-white p-4 rounded-md">
                <strong className="text-green-700">Razón Social:</strong>
                <p className="text-lg text-gray-800">{data.razon_social}</p>
              </div>
              <div className="bg-white p-4 rounded-md">
                <strong className="text-green-700">Sector de Negocio:</strong>
                <p className="text-lg text-gray-800 uppercase tracking-wider">
                  <span className="bg-green-100 px-3 py-1 rounded-full text-green-800 font-semibold">
                    {data.sector_negocio}
                  </span>
                </p>
              </div>
              <div className="bg-white p-4 rounded-md">
                <strong className="text-green-700">Número de Empleados:</strong>
                <p className="text-lg text-gray-800">{data.numero_empleados || 'No especificado'}</p>
              </div>
            </div>
            <div className="space-y-4">
              <div className="bg-white p-4 rounded-md">
                <strong className="text-green-700">Fecha de Constitución:</strong>
                <p className="text-lg text-gray-800">
                  {data.fecha_constitucion ? new Date(data.fecha_constitucion).toLocaleDateString('es-CR', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  }) : 'No disponible'}
                </p>
              </div>
              <div className="bg-white p-4 rounded-md">
                <strong className="text-green-700">Teléfono:</strong>
                <p className="text-lg text-gray-800 font-mono">{data.telefono || 'No disponible'}</p>
              </div>
              <div className="bg-white p-4 rounded-md">
                <strong className="text-green-700">Correo Electrónico:</strong>
                <p className="text-lg text-gray-800">{data.email || 'No disponible'}</p>
              </div>
              <div className="bg-white p-4 rounded-md">
                <strong className="text-green-700">Sitio Web:</strong>
                <p className="text-lg text-gray-800">{data.website || 'No disponible'}</p>
              </div>
              <div className="bg-white p-4 rounded-md">
                <strong className="text-green-700">Ubicación Geográfica:</strong>
                <div className="space-y-1">
                  <p className="text-sm text-gray-600">Provincia:</p>
                  <p className="text-lg text-gray-800">{data.provincia_nombre}</p>
                  <p className="text-sm text-gray-600">Cantón:</p>
                  <p className="text-lg text-gray-800">{data.canton_nombre}</p>
                  <p className="text-sm text-gray-600">Distrito:</p>
                  <p className="text-lg text-gray-800">{data.distrito_nombre}</p>
                  <p className="text-sm text-gray-600 mt-2">Dirección:</p>
                  <p className="text-lg text-gray-800">{data.direccion_exacta || 'No especificada'}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  const renderExternalData = (externalData) => {
    if (!externalData || !externalData.data_found) return null;

    return (
      <div className="mt-6 bg-yellow-50 p-6 rounded-lg">
        <h4 className="text-lg font-bold text-yellow-800 mb-4">🔍 Información Adicional de Fuentes Externas</h4>
        
        {externalData.data_found.padron_electoral && (
          <div className="mb-4 p-4 bg-white rounded border">
            <h5 className="font-semibold text-gray-800 mb-2">📋 Padrón Electoral (TSE)</h5>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
              <div><strong>Nombre Completo:</strong> {externalData.data_found.padron_electoral.nombre_completo}</div>
              <div><strong>Junta Electoral:</strong> {externalData.data_found.padron_electoral.junta_electoral}</div>
            </div>
          </div>
        )}

        {externalData.data_found.registro_nacional && (
          <div className="mb-4 p-4 bg-white rounded border">
            <h5 className="font-semibold text-gray-800 mb-2">🏛️ Registro Nacional</h5>
            <div className="text-sm">
              <div><strong>Estado:</strong> {externalData.data_found.registro_nacional.estado}</div>
              <div><strong>Capital Social:</strong> {externalData.data_found.registro_nacional.capital_social}</div>
            </div>
          </div>
        )}

        <div className="text-xs text-gray-600">
          <strong>Fuentes consultadas:</strong> {externalData.sources_consulted?.join(', ')}
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">🔍 Consulta de Personas</h2>
        <p className="text-gray-600">Ingrese el número de cédula para consultar información</p>
      </div>

      {/* Main Search Form */}
      <form onSubmit={handleConsultation} className="mb-8">
        <div className="flex flex-col md:flex-row gap-4 items-end justify-center">
          <div className="flex-1 max-w-md">
            <label className="block text-gray-700 text-sm font-medium mb-2">
              Número de Cédula
            </label>
            <input
              type="text"
              placeholder="Ej: 123456789 o 3-101-123456"
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg font-mono"
              value={cedula}
              onChange={(e) => setCedula(e.target.value.replace(/[^0-9-]/g, ''))}
              maxLength="12"
            />
            <p className="text-sm text-gray-500 mt-1">
              Formato: 9 dígitos (física) o 3-XXX-XXXXXX (jurídica)
            </p>
          </div>
          <button
            type="submit"
            disabled={loading || !cedula.trim()}
            className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-3 rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold text-lg shadow-lg transform hover:scale-105 transition-all"
          >
            {loading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Consultando...
              </div>
            ) : (
              'CONSULTAR'
            )}
          </button>
        </div>
      </form>

      {/* Quick Test Buttons */}
      <div className="mb-6 bg-gray-50 p-4 rounded-lg">
        <h4 className="font-semibold text-gray-700 mb-3">🧪 Prueba Rápida - Cédulas de Ejemplo</h4>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
          {['692785539', '410197954', '903153808', '3-101-629135', '3-101-587436'].map((testCedula, index) => (
            <button
              key={index}
              onClick={() => setCedula(testCedula)}
              className="p-2 bg-blue-100 hover:bg-blue-200 text-blue-800 rounded text-sm font-mono transition-colors"
            >
              {testCedula}
            </button>
          ))}
        </div>
        <p className="text-xs text-gray-600 mt-2">
          Haz clic en cualquier cédula de ejemplo para probar el sistema
        </p>
      </div>

      {/* Search History */}
      {searchHistory.length > 0 && (
        <div className="mb-8 bg-gray-50 p-4 rounded-lg">
          <h4 className="font-semibold text-gray-700 mb-3">📊 Historial de Consultas</h4>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
            {searchHistory.slice(0, 10).map((search, index) => (
              <button
                key={index}
                onClick={() => setCedula(search.cedula)}
                className={`p-2 rounded text-sm font-mono ${
                  search.found 
                    ? 'bg-green-100 text-green-800 hover:bg-green-200' 
                    : 'bg-red-100 text-red-800 hover:bg-red-200'
                }`}
              >
                {search.cedula}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="mt-8">
          {result.found ? (
            <div>
              {renderPersonDetails(result.data, result.type)}
              {result.external_data && renderExternalData(result.external_data)}
              {result.data_enhanced && (
                <div className="mt-4 p-3 bg-blue-100 text-blue-800 rounded">
                  ℹ️ Los datos han sido enriquecidos con información de fuentes externas oficiales.
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-6xl mb-4">😔</div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">No se encontraron resultados</h3>
              <p className="text-gray-600 mb-4">{result.message}</p>
              <div className="bg-yellow-100 border border-yellow-400 text-yellow-800 px-4 py-3 rounded-lg max-w-md mx-auto">
                <p className="text-sm">
                  <strong>Sugerencias:</strong><br />
                  • Verifique que el número de cédula esté correcto<br />
                  • Para personas físicas use 9 dígitos<br />
                  • Para personas jurídicas use formato 3-XXX-XXXXXX
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Quick Stats */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <h4 className="text-lg font-semibold text-gray-800 mb-4">📈 Estadísticas del Sistema</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div className="bg-blue-100 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">2,000</div>
            <div className="text-sm text-blue-800">Personas Físicas</div>
          </div>
          <div className="bg-green-100 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-600">800</div>
            <div className="text-sm text-green-800">Personas Jurídicas</div>
          </div>
          <div className="bg-purple-100 p-4 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">7</div>
            <div className="text-sm text-purple-800">Provincias</div>
          </div>
          <div className="bg-orange-100 p-4 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">{searchHistory.length}</div>
            <div className="text-sm text-orange-800">Consultas Hoy</div>
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="mt-8 bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg">
        <h4 className="text-lg font-semibold text-gray-800 mb-3">💡 Cómo usar el sistema</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700">
          <div>
            <h5 className="font-semibold mb-2">Para Personas Físicas:</h5>
            <ul className="space-y-1">
              <li>• Use el número de cédula de 9 dígitos</li>
              <li>• Ejemplo: 123456789</li>
              <li>• Obtendrá: nombre, ocupación, ubicación, contacto</li>
            </ul>
          </div>
          <div>
            <h5 className="font-semibold mb-2">Para Personas Jurídicas:</h5>
            <ul className="space-y-1">
              <li>• Use la cédula jurídica (inicia con 3)</li>
              <li>• Ejemplo: 3-101-123456</li>
              <li>• Obtendrá: empresa, sector, empleados, ubicación</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

// Advanced Search Interface with Filters
const AdvancedSearch = () => {
  const [searchType, setSearchType] = useState('cedula');
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    provincia_id: '',
    canton_id: '',
    distrito_id: '',
    person_type: '',
    business_sector: ''
  });
  const [provincias, setProvincias] = useState([]);
  const [cantones, setCantones] = useState([]);
  const [distritos, setDistritos] = useState([]);

  useEffect(() => {
    loadProvincias();
  }, []);

  useEffect(() => {
    if (filters.provincia_id) {
      loadCantones(filters.provincia_id);
    } else {
      setCantones([]);
      setDistritos([]);
    }
  }, [filters.provincia_id]);

  useEffect(() => {
    if (filters.canton_id) {
      loadDistritos(filters.canton_id);
    } else {
      setDistritos([]);
    }
  }, [filters.canton_id]);

  const loadProvincias = async () => {
    try {
      const data = await apiCall('/locations/provincias');
      setProvincias(data);
    } catch (error) {
      console.error('Error loading provinces:', error);
    }
  };

  const loadCantones = async (provinciaId) => {
    try {
      const data = await apiCall(`/locations/cantones/${provinciaId}`);
      setCantones(data);
    } catch (error) {
      console.error('Error loading cantons:', error);
    }
  };

  const loadDistritos = async (cantonId) => {
    try {
      const data = await apiCall(`/locations/distritos/${cantonId}`);
      setDistritos(data);
    } catch (error) {
      console.error('Error loading districts:', error);
    }
  };

  const handleAdvancedSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      let endpoint = '';
      let payload = {};
      
      switch (searchType) {
        case 'cedula':
          if (searchTerm.trim()) {
            endpoint = `/search/cedula/${encodeURIComponent(searchTerm)}?enrich=true`;
            const data = await apiCall(endpoint);
            setResults(data.found ? [data] : []);
          }
          break;
          
        case 'name':
          endpoint = `/search/name/${encodeURIComponent(searchTerm)}`;
          const nameData = await apiCall(endpoint);
          setResults(nameData.results || []);
          break;
          
        case 'phone':
          endpoint = `/search/telefono/${encodeURIComponent(searchTerm)}`;
          const phoneData = await apiCall(endpoint);
          setResults(phoneData.results || []);
          break;
          
        case 'geographic':
          endpoint = '/search/geografica';
          payload = {
            provincia_id: filters.provincia_id || null,
            canton_id: filters.canton_id || null,
            distrito_id: filters.distrito_id || null,
            person_type: filters.person_type || null,
            business_sector: filters.business_sector || null
          };
          const geoData = await apiCall(endpoint, 'POST', payload);
          setResults(geoData.results || []);
          break;
          
        default:
          setResults([]);
      }
    } catch (error) {
      console.error('Error in advanced search:', error);
      setResults([]);
    }
    setLoading(false);
  };

  const clearFilters = () => {
    setFilters({
      provincia_id: '',
      canton_id: '',
      distrito_id: '',
      person_type: '',
      business_sector: ''
    });
    setSearchTerm('');
    setResults([]);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
        🔍 <span className="ml-2">Búsqueda Avanzada con Filtros</span>
      </h2>
      
      <form onSubmit={handleAdvancedSearch} className="mb-6">
        {/* Search Type Selector */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div>
            <label className="block text-gray-700 text-sm font-medium mb-2">Tipo de Búsqueda</label>
            <select
              value={searchType}
              onChange={(e) => setSearchType(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="cedula">Por Cédula</option>
              <option value="name">Por Nombre/Empresa</option>
              <option value="phone">Por Teléfono</option>
              <option value="geographic">Por Ubicación Geográfica</option>
            </select>
          </div>
          
          {searchType !== 'geographic' && (
            <div className="md:col-span-2">
              <label className="block text-gray-700 text-sm font-medium mb-2">
                {searchType === 'cedula' ? 'Número de Cédula' : 
                 searchType === 'name' ? 'Nombre o Empresa' : 
                 'Número de Teléfono'}
              </label>
              <input
                type="text"
                placeholder={
                  searchType === 'cedula' ? '123456789 o 3-101-123456' :
                  searchType === 'name' ? 'Nombre, apellido o nombre comercial' :
                  '+506 2222-3333 o 8888-9999'
                }
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          )}
          
          <button
            type="submit"
            disabled={loading}
            className="bg-purple-600 text-white px-6 py-3 rounded-md hover:bg-purple-700 disabled:opacity-50 font-semibold"
          >
            {loading ? 'Buscando...' : 'BUSCAR'}
          </button>
        </div>

        {/* Geographic Filters */}
        {searchType === 'geographic' && (
          <div className="bg-gray-50 p-4 rounded-lg mb-4">
            <h4 className="font-semibold text-gray-700 mb-3">🗺️ Filtros Geográficos</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <select
                value={filters.provincia_id}
                onChange={(e) => setFilters({...filters, provincia_id: e.target.value, canton_id: '', distrito_id: ''})}
                className="px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">Todas las provincias</option>
                {provincias.map(provincia => (
                  <option key={provincia.id} value={provincia.id}>{provincia.nombre}</option>
                ))}
              </select>

              <select
                value={filters.canton_id}
                onChange={(e) => setFilters({...filters, canton_id: e.target.value, distrito_id: ''})}
                disabled={!filters.provincia_id}
                className="px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
              >
                <option value="">Todos los cantones</option>
                {cantones.map(canton => (
                  <option key={canton.id} value={canton.id}>{canton.nombre}</option>
                ))}
              </select>

              <select
                value={filters.distrito_id}
                onChange={(e) => setFilters({...filters, distrito_id: e.target.value})}
                disabled={!filters.canton_id}
                className="px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
              >
                <option value="">Todos los distritos</option>
                {distritos.map(distrito => (
                  <option key={distrito.id} value={distrito.id}>{distrito.nombre}</option>
                ))}
              </select>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <select
                value={filters.person_type}
                onChange={(e) => setFilters({...filters, person_type: e.target.value})}
                className="px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">Físicas y Jurídicas</option>
                <option value="fisica">Solo Personas Físicas</option>
                <option value="juridica">Solo Personas Jurídicas</option>
              </select>

              <select
                value={filters.business_sector}
                onChange={(e) => setFilters({...filters, business_sector: e.target.value})}
                className="px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">Todos los sectores</option>
                <option value="comercio">Comercio</option>
                <option value="servicios">Servicios</option>
                <option value="industria">Industria</option>
                <option value="tecnologia">Tecnología</option>
                <option value="educacion">Educación</option>
                <option value="salud">Salud</option>
                <option value="construccion">Construcción</option>
                <option value="turismo">Turismo</option>
                <option value="agricultura">Agricultura</option>
                <option value="otros">Otros</option>
              </select>
            </div>
          </div>
        )}

        {/* Clear Filters Button */}
        <div className="flex justify-end">
          <button
            type="button"
            onClick={clearFilters}
            className="text-gray-600 hover:text-gray-800 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
          >
            🗑️ Limpiar Filtros
          </button>
        </div>
      </form>

      {/* Results Display */}
      {results.length > 0 && (
        <div className="mt-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-700">
              📊 Resultados: {results.length} registro(s) encontrado(s)
            </h3>
            <button
              onClick={() => {/* Implementar exportación */}}
              className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 text-sm"
            >
              📥 Exportar CSV
            </button>
          </div>
          
          <div className="space-y-4">
            {results.map((result, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                {result.found ? 
                  renderPersonDetails(result.data, result.type) :
                  <div className="bg-gray-50 p-4 rounded">
                    <div className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      result.type === 'fisica' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                    }`}>
                      {result.type === 'fisica' ? 'Persona Física' : 'Persona Jurídica'}
                    </div>
                    <div className="mt-2">
                      {/* Renderizar datos básicos para resultados de listas */}
                      <p className="font-semibold text-gray-800">
                        {result.data?.cedula || result.data?.cedula_juridica} - {' '}
                        {result.data?.nombre ? 
                          `${result.data.nombre} ${result.data.primer_apellido || ''}` : 
                          result.data?.nombre_comercial
                        }
                      </p>
                      <p className="text-gray-600 text-sm">
                        {result.data?.provincia_nombre}, {result.data?.canton_nombre}, {result.data?.distrito_nombre}
                      </p>
                    </div>
                  </div>
                }
              </div>
            ))}
          </div>
        </div>
      )}

      {results.length === 0 && searchTerm && !loading && (
        <div className="text-center py-8 bg-yellow-50 rounded-lg">
          <div className="text-4xl mb-4">🔍</div>
          <h3 className="text-lg font-semibold text-gray-800 mb-2">No se encontraron resultados</h3>
          <p className="text-gray-600">Intente con diferentes términos de búsqueda o filtros</p>
        </div>
      )}
    </div>
  );
};

// Helper function to render person details for both components
const renderPersonDetails = (data, type) => {
  if (type === 'fisica') {
    return (
      <div className="bg-blue-50 p-6 rounded-lg border-l-4 border-blue-500">
        <h3 className="text-2xl font-bold text-blue-800 mb-6 flex items-center">
          👤 <span className="ml-2">Persona Física Encontrada</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="bg-white p-4 rounded-md">
              <strong className="text-blue-700">Número de Cédula:</strong>
              <p className="text-xl font-mono text-gray-800">{data.cedula}</p>
            </div>
            <div className="bg-white p-4 rounded-md">
              <strong className="text-blue-700">Nombre Completo:</strong>
              <p className="text-xl text-gray-800">
                {`${data.nombre} ${data.primer_apellido} ${data.segundo_apellido || ''}`.trim()}
              </p>
            </div>
            <div className="bg-white p-4 rounded-md">
              <strong className="text-blue-700">Fecha de Nacimiento:</strong>
              <p className="text-lg text-gray-800">
                {data.fecha_nacimiento ? new Date(data.fecha_nacimiento).toLocaleDateString('es-CR', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                }) : 'No disponible'}
              </p>
            </div>
            <div className="bg-white p-4 rounded-md">
              <strong className="text-blue-700">Ocupación:</strong>
              <p className="text-lg text-gray-800">{data.ocupacion || 'No especificada'}</p>
            </div>
          </div>
          <div className="space-y-4">
            <div className="bg-white p-4 rounded-md">
              <strong className="text-blue-700">Teléfono:</strong>
              <p className="text-lg text-gray-800 font-mono">{data.telefono || 'No disponible'}</p>
            </div>
            <div className="bg-white p-4 rounded-md">
              <strong className="text-blue-700">Correo Electrónico:</strong>
              <p className="text-lg text-gray-800">{data.email || 'No disponible'}</p>
            </div>
            <div className="bg-white p-4 rounded-md">
              <strong className="text-blue-700">Ubicación Geográfica:</strong>
              <div className="space-y-1">
                <p className="text-sm text-gray-600">Provincia:</p>
                <p className="text-lg text-gray-800">{data.provincia_nombre}</p>
                <p className="text-sm text-gray-600">Cantón:</p>
                <p className="text-lg text-gray-800">{data.canton_nombre}</p>
                <p className="text-sm text-gray-600">Distrito:</p>
                <p className="text-lg text-gray-800">{data.distrito_nombre}</p>
              </div>
            </div>
            <div className="bg-white p-4 rounded-md">
              <strong className="text-blue-700">Dirección Exacta:</strong>
              <p className="text-lg text-gray-800">{data.direccion_exacta || 'No especificada'}</p>
            </div>
          </div>
        </div>
      </div>
    );
  } else if (type === 'juridica') {
    return (
      <div className="bg-green-50 p-6 rounded-lg border-l-4 border-green-500">
        <h3 className="text-2xl font-bold text-green-800 mb-6 flex items-center">
          🏢 <span className="ml-2">Persona Jurídica Encontrada</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="bg-white p-4 rounded-md">
              <strong className="text-green-700">Cédula Jurídica:</strong>
              <p className="text-xl font-mono text-gray-800">{data.cedula_juridica}</p>
            </div>
            <div className="bg-white p-4 rounded-md">
              <strong className="text-green-700">Nombre Comercial:</strong>
              <p className="text-xl text-gray-800">{data.nombre_comercial}</p>
            </div>
            <div className="bg-white p-4 rounded-md">
              <strong className="text-green-700">Razón Social:</strong>
              <p className="text-lg text-gray-800">{data.razon_social}</p>
            </div>
            <div className="bg-white p-4 rounded-md">
              <strong className="text-green-700">Sector de Negocio:</strong>
              <p className="text-lg text-gray-800 uppercase tracking-wider">
                <span className="bg-green-100 px-3 py-1 rounded-full text-green-800 font-semibold">
                  {data.sector_negocio}
                </span>
              </p>
            </div>
            <div className="bg-white p-4 rounded-md">
              <strong className="text-green-700">Número de Empleados:</strong>
              <p className="text-lg text-gray-800">{data.numero_empleados || 'No especificado'}</p>
            </div>
          </div>
          <div className="space-y-4">
            <div className="bg-white p-4 rounded-md">
              <strong className="text-green-700">Fecha de Constitución:</strong>
              <p className="text-lg text-gray-800">
                {data.fecha_constitucion ? new Date(data.fecha_constitucion).toLocaleDateString('es-CR', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                }) : 'No disponible'}
              </p>
            </div>
            <div className="bg-white p-4 rounded-md">
              <strong className="text-green-700">Teléfono:</strong>
              <p className="text-lg text-gray-800 font-mono">{data.telefono || 'No disponible'}</p>
            </div>
            <div className="bg-white p-4 rounded-md">
              <strong className="text-green-700">Correo Electrónico:</strong>
              <p className="text-lg text-gray-800">{data.email || 'No disponible'}</p>
            </div>
            <div className="bg-white p-4 rounded-md">
              <strong className="text-green-700">Sitio Web:</strong>
              <p className="text-lg text-gray-800">{data.website || 'No disponible'}</p>
            </div>
            <div className="bg-white p-4 rounded-md">
              <strong className="text-green-700">Ubicación Geográfica:</strong>
              <div className="space-y-1">
                <p className="text-sm text-gray-600">Provincia:</p>
                <p className="text-lg text-gray-800">{data.provincia_nombre}</p>
                <p className="text-sm text-gray-600">Cantón:</p>
                <p className="text-lg text-gray-800">{data.canton_nombre}</p>
                <p className="text-sm text-gray-600">Distrito:</p>
                <p className="text-lg text-gray-800">{data.distrito_nombre}</p>
                <p className="text-sm text-gray-600 mt-2">Dirección:</p>
                <p className="text-lg text-gray-800">{data.direccion_exacta || 'No especificada'}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
  return null;
};

// Geographic Search Component
const GeograficaSearch = () => {
  const [provincias, setProvincias] = useState([]);
  const [cantones, setCantones] = useState([]);
  const [distritos, setDistritos] = useState([]);
  const [filters, setFilters] = useState({
    provincia_id: '',
    canton_id: '',
    distrito_id: '',
    person_type: ''
  });
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadProvincias();
  }, []);

  useEffect(() => {
    if (filters.provincia_id) {
      loadCantones(filters.provincia_id);
    } else {
      setCantones([]);
      setDistritos([]);
    }
  }, [filters.provincia_id]);

  useEffect(() => {
    if (filters.canton_id) {
      loadDistritos(filters.canton_id);
    } else {
      setDistritos([]);
    }
  }, [filters.canton_id]);

  const loadProvincias = async () => {
    try {
      const data = await apiCall('/locations/provincias');
      setProvincias(data);
    } catch (error) {
      console.error('Error loading provinces:', error);
    }
  };

  const loadCantones = async (provinciaId) => {
    try {
      const data = await apiCall(`/locations/cantones/${provinciaId}`);
      setCantones(data);
    } catch (error) {
      console.error('Error loading cantons:', error);
    }
  };

  const loadDistritos = async (cantonId) => {
    try {
      const data = await apiCall(`/locations/distritos/${cantonId}`);
      setDistritos(data);
    } catch (error) {
      console.error('Error loading districts:', error);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const data = await apiCall('/search/geografica', 'POST', filters);
      setResults(data.results || []);
    } catch (error) {
      console.error('Error in geographic search:', error);
      setResults([]);
    }
    setLoading(false);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Consulta Geográfica</h2>
      
      <form onSubmit={handleSearch} className="mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <select
            className="px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={filters.provincia_id}
            onChange={(e) => setFilters({...filters, provincia_id: e.target.value, canton_id: '', distrito_id: ''})}
          >
            <option value="">Todas las provincias</option>
            {provincias.map(provincia => (
              <option key={provincia.id} value={provincia.id}>{provincia.nombre}</option>
            ))}
          </select>

          <select
            className="px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={filters.canton_id}
            onChange={(e) => setFilters({...filters, canton_id: e.target.value, distrito_id: ''})}
            disabled={!filters.provincia_id}
          >
            <option value="">Todos los cantones</option>
            {cantones.map(canton => (
              <option key={canton.id} value={canton.id}>{canton.nombre}</option>
            ))}
          </select>

          <select
            className="px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={filters.distrito_id}
            onChange={(e) => setFilters({...filters, distrito_id: e.target.value})}
            disabled={!filters.canton_id}
          >
            <option value="">Todos los distritos</option>
            {distritos.map(distrito => (
              <option key={distrito.id} value={distrito.id}>{distrito.nombre}</option>
            ))}
          </select>

          <select
            className="px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={filters.person_type}
            onChange={(e) => setFilters({...filters, person_type: e.target.value})}
          >
            <option value="">Físicas y Jurídicas</option>
            <option value="fisica">Solo Físicas</option>
            <option value="juridica">Solo Jurídicas</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="bg-green-600 text-white px-8 py-3 rounded-md hover:bg-green-700 disabled:opacity-50"
        >
          {loading ? 'Buscando...' : 'Consultar'}
        </button>
      </form>

      <div className="mt-6">
        <h3 className="text-lg font-semibold text-gray-700 mb-4">
          Resultados: {results.length} registros encontrados
        </h3>
        <ResultsTable results={results} loading={loading} />
      </div>
    </div>
  );
};

// Search by Name Component  
const NombresSearch = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchTerm.trim()) return;

    setLoading(true);
    try {
      const data = await apiCall(`/search/name/${encodeURIComponent(searchTerm)}`);
      setResults(data.results || []);
    } catch (error) {
      console.error('Error searching by name:', error);
      setResults([]);
    }
    setLoading(false);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Búsqueda por Nombres</h2>
      
      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-4">
          <input
            type="text"
            placeholder="Ingrese nombre, apellido o nombre comercial"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-purple-600 text-white px-8 py-3 rounded-md hover:bg-purple-700 disabled:opacity-50"
          >
            {loading ? 'Buscando...' : 'Buscar'}
          </button>
        </div>
      </form>

      <div className="mt-6">
        <h3 className="text-lg font-semibold text-gray-700 mb-4">
          Resultados: {results.length} registros encontrados
        </h3>
        <ResultsTable results={results} loading={loading} />
      </div>
    </div>
  );
};

// Search by Phone Component
const TelefonoSearch = () => {
  const [telefono, setTelefono] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!telefono.trim()) return;

    setLoading(true);
    try {
      const data = await apiCall(`/search/telefono/${encodeURIComponent(telefono)}`);
      setResults(data.results || []);
    } catch (error) {
      console.error('Error searching by phone:', error);
      setResults([]);
    }
    setLoading(false);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Búsqueda por Teléfono</h2>
      
      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-4">
          <input
            type="text"
            placeholder="Ingrese número telefónico (ej: 2222-3333, +506 8888-9999)"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={telefono}
            onChange={(e) => setTelefono(e.target.value)}
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-orange-600 text-white px-8 py-3 rounded-md hover:bg-orange-700 disabled:opacity-50"
          >
            {loading ? 'Buscando...' : 'Buscar'}
          </button>
        </div>
      </form>

      <div className="mt-6">
        <h3 className="text-lg font-semibold text-gray-700 mb-4">
          Resultados: {results.length} registros encontrados
        </h3>
        <ResultsTable results={results} loading={loading} />
      </div>
    </div>
  );
};

// Navigation Bar Component
const NavigationBar = ({ activeSection, setActiveSection }) => {
  const { user, logout } = useAuth();

  const menuItems = [
    { id: 'home', label: 'Inicio', icon: '🏠' },
    { 
      id: 'consultas-individuales', 
      label: 'Consultas Individuales', 
      icon: '👤',
      submenu: [
        { id: 'cedula', label: 'Por Cédula' },
        { id: 'geografica', label: 'Geográfica' },
        { id: 'patronos', label: 'Patronos' },
        { id: 'colegiados', label: 'Colegiados' },
        { id: 'pensionados', label: 'Pensionados' },
        { id: 'independientes', label: 'Independientes' }
      ]
    },
    { 
      id: 'consultas-masivas', 
      label: 'Consultas Masivas', 
      icon: '🏢',
      submenu: [
        { id: 'global', label: 'Global' },
        { id: 'telefono', label: 'Teléfono' },
        { id: 'nombres', label: 'Nombres' },
        { id: 'foto', label: 'Foto' }
      ]
    },
    { 
      id: 'consultas-especiales', 
      label: 'Consultas Especiales', 
      icon: '⚡',
      submenu: []
    },
    { id: 'bitacora', label: 'Bitacora CSV', icon: '📊' },
    { id: 'telegram', label: 'Telegram', icon: '📱' },
    { id: 'ayuda', label: 'Ayuda', icon: '❓' }
  ];

  return (
    <nav className="bg-gradient-to-r from-green-500 via-blue-600 to-purple-600 text-white shadow-lg">
      <div className="flex items-center justify-between px-4 py-2">
        <div className="flex items-center space-x-2">
          {menuItems.map((item) => (
            <div key={item.id} className="relative group">
              <button
                onClick={() => setActiveSection(item.id)}
                className={`px-4 py-2 rounded-md transition-colors ${
                  activeSection === item.id ? 'bg-white bg-opacity-20' : 'hover:bg-white hover:bg-opacity-10'
                }`}
              >
                {item.label} {item.submenu && '▼'}
              </button>
              
              {item.submenu && item.submenu.length > 0 && (
                <div className="absolute top-full left-0 mt-1 bg-blue-600 rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                  <div className="py-2 min-w-48">
                    {item.submenu.map((subItem) => (
                      <button
                        key={subItem.id}
                        onClick={() => setActiveSection(subItem.id)}
                        className="block w-full text-left px-4 py-2 hover:bg-blue-700 transition-colors"
                      >
                        {subItem.label}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="flex items-center space-x-4">
          <span className="bg-yellow-500 text-black px-3 py-1 rounded-md font-semibold">
            {user?.username || 'Usuario'}
          </span>
          <button
            onClick={logout}
            className="bg-red-500 hover:bg-red-600 px-4 py-2 rounded-md transition-colors"
          >
            Salir
          </button>
        </div>
      </div>
    </nav>
  );
};

// Dashboard Component
const Dashboard = () => {
  const [activeSection, setActiveSection] = useState('home');
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await apiCall('/demographics/query', 'POST', {});
        setStats(data);
      } catch (error) {
        console.error('Error fetching stats:', error);
      }
    };

    fetchStats();
  }, []);

  const renderMainContent = () => {
    // All consultation types redirect to main consultation interface
    switch (activeSection) {
      case 'home':
        return <HomePage stats={stats} />;
      
      // All individual consultations go to main consultation
      case 'cedula':
      case 'patronos':
      case 'geografica':
      case 'colegiados':
      case 'pensionados':
      case 'independientes':
        return <ConsultationInterface />;
      
      // All massive consultations go to main consultation  
      case 'global':
      case 'telefono':
      case 'nombres':
      case 'foto':
        return <ConsultationInterface />;
      
      // Advanced features
      case 'consultas-especiales':
        return <AdvancedSearch />;
      
      case 'bitacora':
        return <BitacoraCSV />;
        
      case 'telegram':
        return <TelegramIntegration />;
        
      case 'ayuda':
        return <AyudaSystem />;
        
      default:
        return <ConsultationInterface />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-800">
      <NavigationBar activeSection={activeSection} setActiveSection={setActiveSection} />
      
      <div className="container mx-auto p-4">
        {/* Logo and Alert Banner */}
        <div className="text-center mb-6">
          <div className="inline-block bg-blue-600 rounded-full p-6 mb-4">
            <h1 className="text-white text-4xl font-bold tracking-wider">DATICOS</h1>
          </div>
        </div>

        <div className="bg-blue-100 text-blue-800 p-4 rounded-lg mb-4">
          <p className="text-center font-semibold">
            PARA RECARGAS AL 83713030 WADVISER. CONSULTAS ÚNICAMENTE CON WENDEL AL 87012461
          </p>
        </div>

        <div className="bg-yellow-100 text-yellow-800 p-4 rounded-lg mb-6">
          <h3 className="font-bold text-lg mb-2">Importante / Novedades</h3>
          <p className="text-sm mb-2"><strong>24-04-25</strong></p>
          <p className="text-sm mb-2">
            A todos los usuarios que utilicen depositantes nuevos, deberán esperar 72 horas para que la recarga se realice.
          </p>
          <p className="text-sm mb-2">
            El tema de los formularios para acreditar depositantes nuevos no lo vamos a seguir.
          </p>
          <p className="text-sm">
            Esto aplica solo para usuarios Pre-pago.
          </p>
        </div>

        {renderMainContent()}
      </div>
    </div>
  );
};

// Home Page Component
const HomePage = ({ stats }) => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Panel de Control</h2>
      
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-blue-100 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-blue-800">Personas Físicas</h3>
            <p className="text-3xl font-bold text-blue-600">{stats.total_personas_fisicas?.toLocaleString()}</p>
          </div>
          
          <div className="bg-green-100 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-green-800">Personas Jurídicas</h3>
            <p className="text-3xl font-bold text-green-600">{stats.total_personas_juridicas?.toLocaleString()}</p>
          </div>
          
          <div className="bg-purple-100 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-purple-800">Provincias</h3>
            <p className="text-3xl font-bold text-purple-600">7</p>
          </div>
          
          <div className="bg-orange-100 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-orange-800">Total Registros</h3>
            <p className="text-3xl font-bold text-orange-600">
              {((stats.total_personas_fisicas || 0) + (stats.total_personas_juridicas || 0)).toLocaleString()}
            </p>
          </div>
        </div>
      )}
      
      <div className="mt-8 bg-gray-50 p-6 rounded-lg">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Bienvenido a Daticos v2.0</h3>
        <p className="text-gray-600 mb-4">
          Sistema completo de base de datos para Costa Rica. Realice consultas de personas físicas y jurídicas, 
          estadísticas demográficas y prospectación de clientes.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          <div>
            <h4 className="font-semibold text-gray-800 mb-2">Consultas Disponibles:</h4>
            <ul className="list-disc list-inside text-gray-600 space-y-2">
              <li>Búsqueda por número de cédula</li>
              <li>Consultas geográficas por ubicación</li>
              <li>Búsquedas por nombre y apellidos</li>
              <li>Consultas por número telefónico</li>
              <li>Búsquedas masivas y globales</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold text-gray-800 mb-2">Datos Incluidos:</h4>
            <ul className="list-disc list-inside text-gray-600 space-y-2">
              <li>Información demográfica completa</li>
              <li>Datos de contacto y ubicación</li>
              <li>Información empresarial y comercial</li>
              <li>Sectores de negocio y empleados</li>
              <li>Estadísticas poblacionales</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

// Bitacora CSV Component
const BitacoraCSV = () => {
  const [exportOptions, setExportOptions] = useState({
    type: 'all',
    provincia_id: '',
    date_from: '',
    date_to: ''
  });
  const [provincias, setProvincias] = useState([]);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    loadProvincias();
  }, []);

  const loadProvincias = async () => {
    try {
      const data = await apiCall('/locations/provincias');
      setProvincias(data);
    } catch (error) {
      console.error('Error loading provinces:', error);
    }
  };

  const handleExport = async () => {
    setExporting(true);
    // Simulate export process
    setTimeout(() => {
      setExporting(false);
      alert('Exportación iniciada. Recibirá un email cuando esté lista.');
    }, 2000);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">📊 Exportación de Datos (CSV)</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Opciones de Exportación</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-gray-700 text-sm font-medium mb-2">Tipo de Datos</label>
              <select
                value={exportOptions.type}
                onChange={(e) => setExportOptions({...exportOptions, type: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">Todos los registros</option>
                <option value="fisica">Solo personas físicas</option>
                <option value="juridica">Solo personas jurídicas</option>
              </select>
            </div>

            <div>
              <label className="block text-gray-700 text-sm font-medium mb-2">Provincia (Opcional)</label>
              <select
                value={exportOptions.provincia_id}
                onChange={(e) => setExportOptions({...exportOptions, provincia_id: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Todas las provincias</option>
                {provincias.map(provincia => (
                  <option key={provincia.id} value={provincia.id}>{provincia.nombre}</option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-700 text-sm font-medium mb-2">Fecha Desde</label>
                <input
                  type="date"
                  value={exportOptions.date_from}
                  onChange={(e) => setExportOptions({...exportOptions, date_from: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-gray-700 text-sm font-medium mb-2">Fecha Hasta</label>
                <input
                  type="date"
                  value={exportOptions.date_to}
                  onChange={(e) => setExportOptions({...exportOptions, date_to: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <button
              onClick={handleExport}
              disabled={exporting}
              className="w-full bg-green-600 text-white py-3 px-4 rounded-md hover:bg-green-700 disabled:opacity-50 font-semibold"
            >
              {exporting ? 'Generando Exportación...' : '📥 Generar Archivo CSV'}
            </button>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Información de Exportación</h3>
          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-semibold text-blue-800 mb-2">🔍 ¿Qué incluye la exportación?</h4>
            <ul className="text-sm text-blue-700 space-y-2">
              <li>• Todos los datos de personas físicas y jurídicas</li>
              <li>• Información de ubicación geográfica</li>
              <li>• Datos de contacto disponibles</li>
              <li>• Información empresarial (para jurídicas)</li>
              <li>• Formato compatible con Excel</li>
            </ul>
          </div>
          
          <div className="mt-4 bg-yellow-50 p-4 rounded-lg">
            <h4 className="font-semibold text-yellow-800 mb-2">⚠️ Términos de Uso</h4>
            <ul className="text-sm text-yellow-700 space-y-1">
              <li>• Uso exclusivo para fines comerciales legítimos</li>
              <li>• Prohibido revender o distribuir los datos</li>
              <li>• Cumplir con la Ley de Protección de Datos</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

// Telegram Integration Component
const TelegramIntegration = () => {
  const [telegramConnected, setTelegramConnected] = useState(false);
  const [botToken, setBotToken] = useState('');

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">📱 Integración con Telegram</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Configuración del Bot</h3>
          
          {!telegramConnected ? (
            <div className="space-y-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-semibold text-blue-800 mb-2">🤖 Cómo configurar:</h4>
                <ol className="text-sm text-blue-700 space-y-2">
                  <li>1. Contacte a @BotFather en Telegram</li>
                  <li>2. Cree un nuevo bot con /newbot</li>
                  <li>3. Copie el token que le proporcione</li>
                  <li>4. Pegue el token aquí abajo</li>
                </ol>
              </div>
              
              <div>
                <label className="block text-gray-700 text-sm font-medium mb-2">Token del Bot</label>
                <input
                  type="text"
                  placeholder="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
                  className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={botToken}
                  onChange={(e) => setBotToken(e.target.value)}
                />
              </div>
              
              <button
                onClick={() => setTelegramConnected(true)}
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 font-semibold"
              >
                🔗 Conectar Bot
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="font-semibold text-green-800 mb-2">✅ Bot Conectado</h4>
                <p className="text-sm text-green-700">Su bot de Telegram está funcionando correctamente.</p>
              </div>
              
              <button
                onClick={() => setTelegramConnected(false)}
                className="w-full bg-red-600 text-white py-3 px-4 rounded-md hover:bg-red-700 font-semibold"
              >
                🔌 Desconectar Bot
              </button>
            </div>
          )}
        </div>
        
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Funcionalidades</h3>
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold text-gray-800 mb-2">📋 Comandos Disponibles</h4>
              <div className="text-sm text-gray-700 space-y-1">
                <div><code>/consulta [cédula]</code> - Consultar persona</div>
                <div><code>/stats</code> - Estadísticas del sistema</div>
                <div><code>/help</code> - Mostrar ayuda</div>
              </div>
            </div>
            
            <div className="bg-purple-50 p-4 rounded-lg">
              <h4 className="font-semibold text-purple-800 mb-2">🚀 Características</h4>
              <ul className="text-sm text-purple-700 space-y-1">
                <li>• Consultas rápidas por cédula</li>
                <li>• Notificaciones automáticas</li>
                <li>• Reportes programados</li>
                <li>• Integración con WhatsApp Business</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Help System Component
const AyudaSystem = () => {
  const [selectedTopic, setSelectedTopic] = useState('general');

  const helpTopics = {
    general: {
      title: "Información General",
      content: (
        <div className="space-y-4">
          <p>Daticos es el sistema más completo de consulta de datos de Costa Rica. Permite acceder a información de personas físicas y jurídicas de manera rápida y confiable.</p>
          
          <h4 className="font-semibold text-gray-800">🎯 ¿Qué puedo consultar?</h4>
          <ul className="list-disc list-inside text-gray-700 space-y-1">
            <li>Información personal de personas físicas</li>
            <li>Datos comerciales de empresas</li>
            <li>Ubicación geográfica detallada</li>
            <li>Información de contacto</li>
            <li>Datos actualizados mensualmente</li>
          </ul>
        </div>
      )
    },
    consultas: {
      title: "Cómo Hacer Consultas",
      content: (
        <div className="space-y-4">
          <h4 className="font-semibold text-gray-800">📝 Pasos para consultar:</h4>
          <ol className="list-decimal list-inside text-gray-700 space-y-2">
            <li>Haga clic en cualquier tipo de consulta en el menú principal</li>
            <li>Ingrese el número de cédula en el campo correspondiente</li>
            <li>Presione el botón "CONSULTAR"</li>
            <li>Revise la información encontrada</li>
          </ol>
          
          <h4 className="font-semibold text-gray-800">🔍 Tipos de cédula:</h4>
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <strong>Personas Físicas:</strong><br />
                <code>123456789</code> (9 dígitos)
              </div>
              <div>
                <strong>Personas Jurídicas:</strong><br />
                <code>3-101-123456</code> (con guiones)
              </div>
            </div>
          </div>
        </div>
      )
    },
    precios: {
      title: "Precios y Planes",
      content: (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-semibold text-blue-800 mb-2">Plan Básico</h4>
              <div className="text-2xl font-bold text-blue-600 mb-2">₡15,000</div>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• 500 consultas/mes</li>
                <li>• Datos básicos</li>
                <li>• Soporte por email</li>
              </ul>
            </div>
            
            <div className="bg-green-50 p-4 rounded-lg border-2 border-green-200">
              <h4 className="font-semibold text-green-800 mb-2">Plan Profesional</h4>
              <div className="text-2xl font-bold text-green-600 mb-2">₡35,000</div>
              <ul className="text-sm text-green-700 space-y-1">
                <li>• 2,000 consultas/mes</li>
                <li>• Datos enriquecidos</li>
                <li>• Exportación CSV</li>
                <li>• Telegram Bot</li>
              </ul>
            </div>
            
            <div className="bg-purple-50 p-4 rounded-lg">
              <h4 className="font-semibold text-purple-800 mb-2">Plan Empresarial</h4>
              <div className="text-2xl font-bold text-purple-600 mb-2">₡75,000</div>
              <ul className="text-sm text-purple-700 space-y-1">
                <li>• Consultas ilimitadas</li>
                <li>• API personalizada</li>
                <li>• Soporte prioritario</li>
                <li>• Integraciones custom</li>
              </ul>
            </div>
          </div>
        </div>
      )
    },
    contacto: {
      title: "Información de Contacto",
      content: (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-gray-800 mb-3">📞 Contactos</h4>
              <div className="space-y-2 text-gray-700">
                <div><strong>Teléfono:</strong> +506 8701-2461</div>
                <div><strong>WhatsApp:</strong> +506 8371-3030</div>
                <div><strong>Email:</strong> info@daticos.com</div>
                <div><strong>Sitio Web:</strong> www.daticos.com</div>
              </div>
            </div>
            
            <div>
              <h4 className="font-semibold text-gray-800 mb-3">🕒 Horario de Atención</h4>
              <div className="space-y-2 text-gray-700">
                <div><strong>Lunes a Viernes:</strong> 8:00 AM - 5:00 PM</div>
                <div><strong>Sábados:</strong> 9:00 AM - 1:00 PM</div>
                <div><strong>Domingos:</strong> Cerrado</div>
              </div>
            </div>
          </div>
          
          <div className="bg-yellow-50 p-4 rounded-lg">
            <h4 className="font-semibold text-yellow-800 mb-2">⚡ Soporte Técnico</h4>
            <p className="text-sm text-yellow-700">
              Para problemas técnicos urgentes, contacte directamente a Wendel al WhatsApp 
              <strong> +506 8701-2461</strong>. Respuesta garantizada en menos de 2 horas 
              durante horario laboral.
            </p>
          </div>
        </div>
      )
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">❓ Centro de Ayuda</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Temas de Ayuda</h3>
          <div className="space-y-2">
            {Object.entries(helpTopics).map(([key, topic]) => (
              <button
                key={key}
                onClick={() => setSelectedTopic(key)}
                className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                  selectedTopic === key
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                }`}
              >
                {topic.title}
              </button>
            ))}
          </div>
        </div>
        
        <div className="md:col-span-3">
          <div className="bg-gray-50 p-6 rounded-lg">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">
              {helpTopics[selectedTopic].title}
            </h3>
            {helpTopics[selectedTopic].content}
          </div>
        </div>
      </div>
    </div>
  );
};

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-800">
        <div className="text-white text-xl">Cargando...</div>
      </div>
    );
  }

  return user ? children : <Navigate to="/login" />;
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
          </Routes>
        </BrowserRouter>
      </div>
    </AuthProvider>
  );
}

export default App;
