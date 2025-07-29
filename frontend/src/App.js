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

// Componente para Consulta con Foto
const ConsultaFoto = () => {
  const [cedula, setCedula] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!cedula.trim()) {
      setError('Por favor ingrese una cédula');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const data = await apiCall(`/search/cedula/${cedula}?enrich=true`);
      setResult(data);
    } catch (error) {
      setError('Error al buscar la cédula: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center mb-6">
        <span className="text-3xl mr-3">📷</span>
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Consulta con Foto</h2>
          <p className="text-gray-600">Búsqueda por cédula con imagen incluida</p>
        </div>
      </div>

      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-4">
          <input
            type="text"
            value={cedula}
            onChange={(e) => setCedula(e.target.value)}
            placeholder="Ingrese número de cédula (ej: 1-0234-0567)"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            maxLength="12"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? '🔍 Buscando...' : '📷 Buscar con Foto'}
          </button>
        </div>
      </form>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          ❌ {error}
        </div>
      )}

      {result && (
        <div className="space-y-4">
          {result.found ? (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-green-800 mb-4">✅ Persona Encontrada</h3>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-2">Información Personal:</h4>
                      <div className="space-y-1 text-sm">
                        <div><strong>Cédula:</strong> {result.data.cedula || 'N/A'}</div>
                        <div><strong>Nombre:</strong> {result.data.nombre || 'N/A'}</div>
                        <div><strong>Apellidos:</strong> {result.data.primer_apellido} {result.data.segundo_apellido}</div>
                        <div><strong>Teléfono:</strong> {result.data.telefono || 'N/A'}</div>
                        <div><strong>Email:</strong> {result.data.email || 'N/A'}</div>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-2">Ubicación:</h4>
                      <div className="space-y-1 text-sm">
                        <div><strong>Provincia:</strong> {result.data.provincia_nombre || 'N/A'}</div>
                        <div><strong>Cantón:</strong> {result.data.canton_nombre || 'N/A'}</div>
                        <div><strong>Distrito:</strong> {result.data.distrito_nombre || 'N/A'}</div>
                        <div><strong>Dirección:</strong> {result.data.direccion_exacta || 'N/A'}</div>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Espacio para foto - simulado */}
                <div className="ml-6 bg-gray-200 border-2 border-dashed border-gray-400 rounded-lg p-4 text-center w-32 h-40 flex flex-col items-center justify-center">
                  <span className="text-4xl mb-2">📷</span>
                  <span className="text-xs text-gray-500">Foto no disponible</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded">
              ❌ No se encontró información para la cédula: {cedula}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Componente para Búsqueda Global
const BusquedaGlobal = () => {
  const [cedula, setCedula] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!cedula.trim()) {
      setError('Por favor ingrese una cédula');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const data = await apiCall(`/search/cedula/${cedula}?enrich=true`);
      setResult(data);
    } catch (error) {
      setError('Error al buscar: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center mb-6">
        <span className="text-3xl mr-3">🌍</span>
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Búsqueda Global</h2>
          <p className="text-gray-600">Consulta completa con enriquecimiento de datos</p>
        </div>
      </div>

      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-4">
          <input
            type="text"
            value={cedula}
            onChange={(e) => setCedula(e.target.value)}
            placeholder="Número de cédula (física: 1-2345-6789, jurídica: 3-101-123456)"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? '🔍 Buscando...' : '🌍 Búsqueda Global'}
          </button>
        </div>
      </form>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          ❌ {error}
        </div>
      )}

      {result && (
        <div className="space-y-6">
          {result.found ? (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-green-800 mb-4">
                ✅ {result.type === 'fisica' ? 'Persona Física' : 'Persona Jurídica'} Encontrada
              </h3>
              
              <div className="grid md:grid-cols-3 gap-6">
                <div className="bg-white rounded-lg p-4 border">
                  <h4 className="font-semibold text-blue-800 mb-3 flex items-center">
                    👤 Información Básica
                  </h4>
                  <div className="space-y-2 text-sm">
                    <div><strong>Cédula:</strong> {result.data.cedula || result.data.cedula_juridica}</div>
                    {result.type === 'fisica' ? (
                      <>
                        <div><strong>Nombre:</strong> {result.data.nombre}</div>
                        <div><strong>Apellidos:</strong> {result.data.primer_apellido} {result.data.segundo_apellido}</div>
                      </>
                    ) : (
                      <>
                        <div><strong>Nombre Comercial:</strong> {result.data.nombre_comercial}</div>
                        <div><strong>Razón Social:</strong> {result.data.razon_social}</div>
                        <div><strong>Sector:</strong> {result.data.sector_negocio}</div>
                      </>
                    )}
                  </div>
                </div>

                <div className="bg-white rounded-lg p-4 border">
                  <h4 className="font-semibold text-blue-800 mb-3 flex items-center">
                    📞 Contacto
                  </h4>
                  <div className="space-y-2 text-sm">
                    <div><strong>Teléfono:</strong> {result.data.telefono || 'N/A'}</div>
                    <div><strong>Email:</strong> {result.data.email || 'N/A'}</div>
                    {result.data.website && (
                      <div><strong>Website:</strong> {result.data.website}</div>
                    )}
                  </div>
                </div>

                <div className="bg-white rounded-lg p-4 border">
                  <h4 className="font-semibold text-blue-800 mb-3 flex items-center">
                    🗺️ Ubicación
                  </h4>
                  <div className="space-y-2 text-sm">
                    <div><strong>Provincia:</strong> {result.data.provincia_nombre}</div>
                    <div><strong>Cantón:</strong> {result.data.canton_nombre}</div>
                    <div><strong>Distrito:</strong> {result.data.distrito_nombre}</div>
                    {result.data.direccion_exacta && (
                      <div><strong>Dirección:</strong> {result.data.direccion_exacta}</div>
                    )}
                  </div>
                </div>
              </div>

              {result.external_data && (
                <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-800 mb-2 flex items-center">
                    🌐 Datos Enriquecidos
                  </h4>
                  <p className="text-blue-700 text-sm">
                    Información adicional obtenida de fuentes externas incluida en los resultados.
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded">
              ❌ No se encontró información para la cédula: {cedula}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Componente para Búsqueda por Teléfono
const BusquedaTelefono = () => {
  const [telefono, setTelefono] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!telefono.trim()) {
      setError('Por favor ingrese un número de teléfono');
      return;
    }

    setLoading(true);
    setError('');
    setResults([]);

    try {
      const data = await apiCall(`/search/telefono/${telefono}`);
      setResults(data.results || []);
    } catch (error) {
      setError('Error al buscar: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center mb-6">
        <span className="text-3xl mr-3">📞</span>
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Búsqueda por Teléfono</h2>
          <p className="text-gray-600">Encuentra personas por número telefónico</p>
        </div>
      </div>

      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-4">
          <input
            type="text"
            value={telefono}
            onChange={(e) => setTelefono(e.target.value)}
            placeholder="Número de teléfono (ej: 8888-8888, 2222-2222, 88888888)"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? '🔍 Buscando...' : '📞 Buscar Teléfono'}
          </button>
        </div>
      </form>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          ❌ {error}
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-700">
            📊 Resultados encontrados: {results.length}
          </h3>
          
          <div className="grid gap-4">
            {results.map((result, index) => (
              <div key={index} className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <span className="text-lg mr-2">
                        {result.type === 'fisica' ? '👤' : '🏢'}
                      </span>
                      <h4 className="font-semibold text-gray-800">
                        {result.type === 'fisica' 
                          ? `${result.data.nombre} ${result.data.primer_apellido} ${result.data.segundo_apellido || ''}`
                          : result.data.nombre_comercial || result.data.razon_social
                        }
                      </h4>
                    </div>
                    
                    <div className="grid md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <div><strong>Cédula:</strong> {result.data.cedula || result.data.cedula_juridica}</div>
                        <div><strong>Teléfono:</strong> {result.data.telefono}</div>
                        {result.data.email && (
                          <div><strong>Email:</strong> {result.data.email}</div>
                        )}
                      </div>
                      <div>
                        <div><strong>Provincia:</strong> {result.data.provincia_nombre}</div>
                        <div><strong>Cantón:</strong> {result.data.canton_nombre}</div>
                        <div><strong>Distrito:</strong> {result.data.distrito_nombre}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {!loading && results.length === 0 && telefono && !error && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded">
          ❌ No se encontraron registros para el teléfono: {telefono}
        </div>
      )}
    </div>
  );
};

// Componente para Búsqueda por Nombres
const BusquedaNombres = () => {
  const [nombre, setNombre] = useState('');
  const [apellido1, setApellido1] = useState('');
  const [apellido2, setApellido2] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    const searchTerm = [nombre, apellido1, apellido2].filter(Boolean).join(' ');
    
    if (!searchTerm.trim()) {
      setError('Por favor ingrese al menos un nombre o apellido');
      return;
    }

    setLoading(true);
    setError('');
    setResults([]);

    try {
      const data = await apiCall(`/search/name/${encodeURIComponent(searchTerm)}`);
      setResults(data.results || []);
    } catch (error) {
      setError('Error al buscar: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center mb-6">
        <span className="text-3xl mr-3">👥</span>
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Búsqueda por Nombres</h2>
          <p className="text-gray-600">Encuentra personas por nombres y apellidos</p>
        </div>
      </div>

      <form onSubmit={handleSearch} className="mb-6">
        <div className="grid md:grid-cols-4 gap-4 mb-4">
          <input
            type="text"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            placeholder="Nombre"
            className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            value={apellido1}
            onChange={(e) => setApellido1(e.target.value)}
            placeholder="Primer Apellido"
            className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            value={apellido2}
            onChange={(e) => setApellido2(e.target.value)}
            placeholder="Segundo Apellido (opcional)"
            className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? '🔍 Buscando...' : '👥 Buscar'}
          </button>
        </div>
      </form>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          ❌ {error}
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-700">
            📊 Resultados encontrados: {results.length}
          </h3>
          
          <div className="grid gap-4">
            {results.map((result, index) => (
              <div key={index} className="bg-gray-50 border border-gray-200 rounded-lg p-4 hover:bg-gray-100 transition-colors">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <span className="text-lg mr-2">
                        {result.type === 'fisica' ? '👤' : '🏢'}
                      </span>
                      <h4 className="font-semibold text-gray-800">
                        {result.type === 'fisica' 
                          ? `${result.data.nombre} ${result.data.primer_apellido} ${result.data.segundo_apellido || ''}`
                          : result.data.nombre_comercial || result.data.razon_social
                        }
                      </h4>
                      <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                        {result.type === 'fisica' ? 'Física' : 'Jurídica'}
                      </span>
                    </div>
                    
                    <div className="grid md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <div><strong>Cédula:</strong> {result.data.cedula || result.data.cedula_juridica}</div>
                        {result.data.telefono && (
                          <div><strong>Teléfono:</strong> {result.data.telefono}</div>
                        )}
                      </div>
                      <div>
                        <div><strong>Provincia:</strong> {result.data.provincia_nombre}</div>
                        <div><strong>Cantón:</strong> {result.data.canton_nombre}</div>
                      </div>
                      <div>
                        <div><strong>Distrito:</strong> {result.data.distrito_nombre}</div>
                        {result.data.email && (
                          <div><strong>Email:</strong> {result.data.email}</div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {!loading && results.length === 0 && (nombre || apellido1 || apellido2) && !error && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded">
          ❌ No se encontraron registros para: {[nombre, apellido1, apellido2].filter(Boolean).join(' ')}
        </div>
      )}
    </div>
  );
};

// Componente para Consultas Masivas - Patronos
const ConsultaPatronos = () => {
  const [filtros, setFiltros] = useState({
    provincia: '',
    canton: '',
    distrito: '',
    sector: '',
    empleados_min: '',
    empleados_max: ''
  });
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [provincias, setProvincias] = useState([]);

  useEffect(() => {
    loadProvincias();
  }, []);

  const loadProvincias = async () => {
    try {
      const data = await apiCall('/locations/provincias');
      setProvincias(data);
    } catch (error) {
      console.error('Error loading provincias:', error);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResults([]);

    try {
      const data = await apiCall('/prospecting/query', 'POST', {
        provincia_id: filtros.provincia || null,
        canton_id: filtros.canton || null,
        distrito_id: filtros.distrito || null,
        sector_negocio: filtros.sector || null,
        min_employees: filtros.empleados_min ? parseInt(filtros.empleados_min) : null,
        max_employees: filtros.empleados_max ? parseInt(filtros.empleados_max) : null
      });
      setResults(data.prospects || []);
    } catch (error) {
      setError('Error en la búsqueda: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center mb-6">
        <span className="text-3xl mr-3">🏢</span>
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Consulta Masiva de Patronos</h2>
          <p className="text-gray-600">Búsqueda avanzada de empresas y patronos por criterios múltiples</p>
        </div>
      </div>

      <form onSubmit={handleSearch} className="mb-6">
        <div className="grid md:grid-cols-3 gap-4 mb-4">
          <select
            value={filtros.provincia}
            onChange={(e) => setFiltros({...filtros, provincia: e.target.value})}
            className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todas las provincias</option>
            {provincias.map(prov => (
              <option key={prov.id} value={prov.id}>{prov.nombre}</option>
            ))}
          </select>

          <select
            value={filtros.sector}
            onChange={(e) => setFiltros({...filtros, sector: e.target.value})}
            className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
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
          </select>

          <div className="flex gap-2">
            <input
              type="number"
              value={filtros.empleados_min}
              onChange={(e) => setFiltros({...filtros, empleados_min: e.target.value})}
              placeholder="Min empleados"
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="number"
              value={filtros.empleados_max}
              onChange={(e) => setFiltros({...filtros, empleados_max: e.target.value})}
              placeholder="Max empleados"
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
        >
          {loading ? '🔍 Consultando...' : '🏢 Consultar Patronos'}
        </button>
      </form>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          ❌ {error}
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-700">
              📊 Patronos encontrados: {results.length}
            </h3>
            <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">
              📤 Exportar CSV
            </button>
          </div>
          
          <div className="grid gap-4">
            {results.map((patron, index) => (
              <div key={index} className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center mb-3">
                      <span className="text-xl mr-3">🏢</span>
                      <div>
                        <h4 className="font-semibold text-gray-800">{patron.nombre_comercial}</h4>
                        <p className="text-sm text-gray-600">{patron.razon_social}</p>
                      </div>
                    </div>
                    
                    <div className="grid md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <div><strong>Cédula Jurídica:</strong> {patron.cedula_juridica}</div>
                        <div><strong>Sector:</strong> {patron.sector_negocio}</div>
                      </div>
                      <div>
                        <div><strong>Empleados:</strong> {patron.numero_empleados || 'N/A'}</div>
                        <div><strong>Teléfono:</strong> {patron.telefono || 'N/A'}</div>
                      </div>
                      <div>
                        <div><strong>Provincia:</strong> {patron.provincia_nombre}</div>
                        <div><strong>Cantón:</strong> {patron.canton_nombre}</div>
                      </div>
                      <div>
                        <div><strong>Email:</strong> {patron.email || 'N/A'}</div>
                        <div><strong>Website:</strong> {patron.website || 'N/A'}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {!loading && results.length === 0 && !error && (
        <div className="text-center py-8 text-gray-500">
          🔍 Use los filtros para buscar patronos y empresas
        </div>
      )}
    </div>
  );
};

// Componente para Búsqueda Geográfica Masiva
const BusquedaGeograficaMasiva = () => {
  const [filtros, setFiltros] = useState({
    provincia: '',
    canton: '',
    distrito: '',
    tipo_persona: ''
  });
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [provincias, setProvincias] = useState([]);
  const [cantones, setCantones] = useState([]);

  useEffect(() => {
    loadProvincias();
  }, []);

  useEffect(() => {
    if (filtros.provincia) {
      loadCantones(filtros.provincia);
    } else {
      setCantones([]);
    }
  }, [filtros.provincia]);

  const loadProvincias = async () => {
    try {
      const data = await apiCall('/locations/provincias');
      setProvincias(data);
    } catch (error) {
      console.error('Error loading provincias:', error);
    }
  };

  const loadCantones = async (provinciaId) => {
    try {
      const data = await apiCall(`/locations/cantones/${provinciaId}`);
      setCantones(data);
    } catch (error) {
      console.error('Error loading cantones:', error);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResults([]);

    try {
      const data = await apiCall('/search/geografica', 'POST', {
        provincia_id: filtros.provincia || null,
        canton_id: filtros.canton || null,
        distrito_id: filtros.distrito || null,
        person_type: filtros.tipo_persona || null
      });
      setResults(data.results || []);
    } catch (error) {
      setError('Error en la búsqueda: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center mb-6">
        <span className="text-3xl mr-3">🗺️</span>
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Búsqueda Geográfica Masiva</h2>
          <p className="text-gray-600">Consulta masiva por ubicación geográfica de Costa Rica</p>
        </div>
      </div>

      <form onSubmit={handleSearch} className="mb-6">
        <div className="grid md:grid-cols-4 gap-4 mb-4">
          <select
            value={filtros.provincia}
            onChange={(e) => setFiltros({...filtros, provincia: e.target.value, canton: ''})}
            className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Seleccionar provincia</option>
            {provincias.map(prov => (
              <option key={prov.id} value={prov.id}>{prov.nombre}</option>
            ))}
          </select>

          <select
            value={filtros.canton}
            onChange={(e) => setFiltros({...filtros, canton: e.target.value})}
            disabled={!filtros.provincia}
            className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
          >
            <option value="">Seleccionar cantón</option>
            {cantones.map(canton => (
              <option key={canton.id} value={canton.id}>{canton.nombre}</option>
            ))}
          </select>

          <select
            value={filtros.tipo_persona}
            onChange={(e) => setFiltros({...filtros, tipo_persona: e.target.value})}
            className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Físicas y Jurídicas</option>
            <option value="fisica">Solo Personas Físicas</option>
            <option value="juridica">Solo Personas Jurídicas</option>
          </select>

          <button
            type="submit"
            disabled={loading || !filtros.provincia}
            className="bg-teal-600 hover:bg-teal-700 text-white px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? '🔍 Buscando...' : '🗺️ Buscar'}
          </button>
        </div>
      </form>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          ❌ {error}
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-700">
              📊 Registros encontrados: {results.length}
            </h3>
            <div className="flex gap-2">
              <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">
                📤 Exportar CSV
              </button>
              <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">
                📊 Estadísticas
              </button>
            </div>
          </div>
          
          <div className="grid gap-3 max-h-96 overflow-y-auto">
            {results.map((result, index) => (
              <div key={index} className="bg-gray-50 border border-gray-200 rounded-lg p-3 hover:bg-gray-100 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <span className="text-lg mr-3">
                      {result.type === 'fisica' ? '👤' : '🏢'}
                    </span>
                    <div>
                      <h4 className="font-semibold text-gray-800 text-sm">
                        {result.type === 'fisica' 
                          ? `${result.data.nombre} ${result.data.primer_apellido} ${result.data.segundo_apellido || ''}`
                          : result.data.nombre_comercial
                        }
                      </h4>
                      <p className="text-xs text-gray-600">
                        {result.data.provincia_nombre} › {result.data.canton_nombre}
                      </p>
                    </div>
                  </div>
                  <div className="text-right text-xs text-gray-600">
                    <div>📄 {result.data.cedula || result.data.cedula_juridica}</div>
                    {result.data.telefono && <div>📞 {result.data.telefono}</div>}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {!loading && results.length === 0 && !error && filtros.provincia && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded">
          🔍 No se encontraron registros para los criterios seleccionados
        </div>
      )}
    </div>
  );
};

// Componente para otras consultas masivas (Colegiados, Pensionados, Independientes)
const ConsultaMasivaTipo = ({ tipo, titulo, descripcion, icono, color }) => {
  const [filtros, setFiltros] = useState({
    provincia: '',
    profesion: '',
    activo: 'todos'
  });
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResults([]);

    // Simular consulta (implementar según endpoint específico)
    try {
      // Placeholder - implementar endpoints específicos
      setTimeout(() => {
        setResults([
          { nombre: 'Ejemplo 1', cedula: '1-1234-5678', profesion: 'Ingeniero', estado: 'Activo' },
          { nombre: 'Ejemplo 2', cedula: '2-2345-6789', profesion: 'Médico', estado: 'Activo' }
        ]);
        setLoading(false);
      }, 1000);
    } catch (error) {
      setError('Error en la búsqueda: ' + error.message);
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center mb-6">
        <span className="text-3xl mr-3">{icono}</span>
        <div>
          <h2 className="text-2xl font-bold text-gray-800">{titulo}</h2>
          <p className="text-gray-600">{descripcion}</p>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h3 className="font-semibold text-blue-800 mb-2">🚧 Función en Desarrollo</h3>
        <p className="text-blue-700 text-sm">
          Esta funcionalidad está siendo implementada con datos reales de {tipo}.
          Pronto estará disponible con consultas masivas completas.
        </p>
      </div>

      <form onSubmit={handleSearch} className="mb-6">
        <div className="grid md:grid-cols-3 gap-4 mb-4">
          <select
            value={filtros.provincia}
            onChange={(e) => setFiltros({...filtros, provincia: e.target.value})}
            className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todas las provincias</option>
            <option value="san-jose">San José</option>
            <option value="alajuela">Alajuela</option>
            <option value="cartago">Cartago</option>
            <option value="heredia">Heredia</option>
            <option value="guanacaste">Guanacaste</option>
            <option value="puntarenas">Puntarenas</option>
            <option value="limon">Limón</option>
          </select>

          <input
            type="text"
            value={filtros.profesion}
            onChange={(e) => setFiltros({...filtros, profesion: e.target.value})}
            placeholder={tipo === 'colegiados' ? 'Profesión o carrera' : tipo === 'pensionados' ? 'Tipo de pensión' : 'Actividad laboral'}
            className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />

          <select
            value={filtros.activo}
            onChange={(e) => setFiltros({...filtros, activo: e.target.value})}
            className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="todos">Todos los estados</option>
            <option value="activo">Solo activos</option>
            <option value="inactivo">Solo inactivos</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={loading}
          className={`${color} text-white px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50`}
        >
          {loading ? '🔍 Consultando...' : `${icono} Consultar ${tipo}`}
        </button>
      </form>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          ❌ {error}
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-700">
            📊 {tipo} encontrados: {results.length}
          </h3>
          
          <div className="grid gap-3">
            {results.map((result, index) => (
              <div key={index} className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                <div className="flex justify-between items-center">
                  <div>
                    <h4 className="font-semibold text-gray-800">{result.nombre}</h4>
                    <p className="text-sm text-gray-600">{result.cedula} • {result.profesion}</p>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    result.estado === 'Activo' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {result.estado}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
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

// Componente para Bloque de Cédulas
const BloqueCedulas = () => {
  const [cedulas, setCedulas] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    
    // Procesar las cédulas ingresadas
    const cedulasList = cedulas.split(/[\n,;]/).map(c => c.trim()).filter(c => c);
    
    if (cedulasList.length === 0) {
      setError('Por favor ingrese al menos una cédula');
      return;
    }

    setLoading(true);
    setError('');
    setResults([]);

    try {
      const searchPromises = cedulasList.map(cedula => 
        apiCall(`/search/cedula/${cedula}`).catch(err => ({ error: err.message, cedula }))
      );
      
      const batchResults = await Promise.all(searchPromises);
      setResults(batchResults);
    } catch (error) {
      setError('Error en la búsqueda masiva: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center mb-6">
        <span className="text-3xl mr-3">🔒</span>
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Bloque de Cédulas Personales</h2>
          <p className="text-gray-600">Consulta masiva de múltiples cédulas simultáneamente</p>
        </div>
      </div>

      <form onSubmit={handleSearch} className="mb-6">
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Cédulas (una por línea, separadas por comas o puntos y comas):
          </label>
          <textarea
            value={cedulas}
            onChange={(e) => setCedulas(e.target.value)}
            placeholder="Ej:
1-1234-5678
2-2345-6789
3-101-123456"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 h-32"
          />
          <p className="text-xs text-gray-500 mt-1">
            Máximo 50 cédulas por consulta
          </p>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
        >
          {loading ? '🔍 Procesando...' : '🔒 Consultar Bloque'}
        </button>
      </form>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          ❌ {error}
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-700">
              📊 Resultados: {results.filter(r => r.found).length} encontradas de {results.length} consultadas
            </h3>
            <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm">
              📤 Exportar Resultados
            </button>
          </div>
          
          <div className="grid gap-3 max-h-96 overflow-y-auto">
            {results.map((result, index) => (
              <div key={index} className={`border rounded-lg p-3 ${
                result.found ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
              }`}>
                {result.found ? (
                  <div>
                    <div className="flex items-center mb-2">
                      <span className="text-green-600 text-lg mr-2">✅</span>
                      <h4 className="font-semibold text-green-800">
                        {result.data.nombre} {result.data.primer_apellido} {result.data.segundo_apellido}
                      </h4>
                    </div>
                    <div className="text-sm text-green-700">
                      <div><strong>Cédula:</strong> {result.data.cedula}</div>
                      <div><strong>Teléfono:</strong> {result.data.telefono || 'N/A'}</div>
                      <div><strong>Ubicación:</strong> {result.data.provincia_nombre}, {result.data.canton_nombre}</div>
                    </div>
                  </div>
                ) : (
                  <div>
                    <div className="flex items-center mb-2">
                      <span className="text-red-600 text-lg mr-2">❌</span>
                      <h4 className="font-semibold text-red-800">
                        {result.cedula || 'Cédula no válida'}
                      </h4>
                    </div>
                    <div className="text-sm text-red-700">
                      No se encontró información para esta cédula
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Componente para Datos Mercantiles
const DatosMercantiles = () => {
  const [cedula, setCedula] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!cedula.trim()) {
      setError('Por favor ingrese una cédula jurídica');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      // Simular datos mercantiles (implementar con datos reales)
      const data = await apiCall(`/search/cedula/${cedula}?enrich=true`);
      
      // Enriquecer con datos mercantiles simulados
      if (data.found && data.type === 'juridica') {
        setResult({
          ...data,
          mercantile_data: {
            registro_mercantil: '12345-2023',
            fecha_inscripcion: '2023-01-15',
            capital_social: '₡5,000,000',
            representante_legal: 'Juan Pérez Rodríguez',
            estado_registro: 'Activo',
            actividades_comerciales: ['Comercio al por menor', 'Servicios profesionales'],
            poderes_registrados: ['Poder General de Administración'],
            hipotecas_registradas: [],
            embargos: []
          }
        });
      } else {
        setResult(data);
      }
    } catch (error) {
      setError('Error al buscar: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center mb-6">
        <span className="text-3xl mr-3">🏬</span>
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Datos Mercantiles</h2>
          <p className="text-gray-600">Información comercial y registros mercantiles</p>
        </div>
      </div>

      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-4">
          <input
            type="text"
            value={cedula}
            onChange={(e) => setCedula(e.target.value)}
            placeholder="Cédula jurídica (ej: 3-101-123456)"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-yellow-600 hover:bg-yellow-700 text-white px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? '🔍 Consultando...' : '🏬 Consultar Mercantil'}
          </button>
        </div>
      </form>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          ❌ {error}
        </div>
      )}

      {result && (
        <div className="space-y-6">
          {result.found ? (
            <div>
              {/* Información básica de la empresa */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <h3 className="text-lg font-semibold text-blue-800 mb-3">🏢 Información de la Empresa</h3>
                <div className="grid md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <div><strong>Nombre Comercial:</strong> {result.data.nombre_comercial}</div>
                    <div><strong>Razón Social:</strong> {result.data.razon_social}</div>
                    <div><strong>Cédula Jurídica:</strong> {result.data.cedula_juridica}</div>
                  </div>
                  <div>
                    <div><strong>Sector:</strong> {result.data.sector_negocio}</div>
                    <div><strong>Teléfono:</strong> {result.data.telefono || 'N/A'}</div>
                    <div><strong>Email:</strong> {result.data.email || 'N/A'}</div>
                  </div>
                </div>
              </div>

              {/* Datos mercantiles específicos */}
              {result.mercantile_data && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-green-800 mb-3">🏬 Datos del Registro Mercantil</h3>
                  
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium text-green-700 mb-2">Registro General:</h4>
                      <div className="space-y-1 text-sm">
                        <div><strong>N° Registro:</strong> {result.mercantile_data.registro_mercantil}</div>
                        <div><strong>Fecha Inscripción:</strong> {result.mercantile_data.fecha_inscripcion}</div>
                        <div><strong>Capital Social:</strong> {result.mercantile_data.capital_social}</div>
                        <div><strong>Estado:</strong> 
                          <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                            {result.mercantile_data.estado_registro}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-green-700 mb-2">Representación Legal:</h4>
                      <div className="space-y-1 text-sm">
                        <div><strong>Representante:</strong> {result.mercantile_data.representante_legal}</div>
                        <div><strong>Poderes Registrados:</strong></div>
                        <ul className="ml-4 list-disc">
                          {result.mercantile_data.poderes_registrados.map((poder, i) => (
                            <li key={i} className="text-xs">{poder}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4">
                    <h4 className="font-medium text-green-700 mb-2">Actividades Comerciales:</h4>
                    <div className="flex flex-wrap gap-2">
                      {result.mercantile_data.actividades_comerciales.map((actividad, i) => (
                        <span key={i} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                          {actividad}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded">
              ❌ No se encontraron datos mercantiles para: {cedula}
            </div>
          )}
        </div>
      )}

      <div className="mt-6 bg-gray-100 rounded-lg p-4">
        <h4 className="font-semibold text-gray-800 mb-2">🚧 Datos Mercantiles en Desarrollo</h4>
        <p className="text-gray-600 text-sm">
          Esta función está siendo integrada con datos reales del Registro Mercantil de Costa Rica.
          Pronto incluirá: hipotecas, embargos, cambios de capital, modificaciones estatutarias, y más.
        </p>
      </div>
    </div>
  );
};

// Componente para Datos Laborales  
const DatosLaborales = () => {
  const [cedula, setCedula] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!cedula.trim()) {
      setError('Por favor ingrese una cédula');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const data = await apiCall(`/search/cedula/${cedula}?enrich=true`);
      
      if (data.found) {
        // Simular datos laborales enriquecidos
        setResult({
          ...data,
          labor_data: {
            empleador_actual: data.data.sector_negocio ? 'Trabajo Independiente' : 'Empresa Privada',
            salario_aproximado: '₡650,000 - ₡850,000',
            antiguedad: '3 años',
            tipo_contrato: 'Indefinido',
            historial_patronos: [
              { empresa: 'Empresa ABC S.A.', periodo: '2021-2024', puesto: 'Analista' },
              { empresa: 'Comercial XYZ Ltda', periodo: '2019-2021', puesto: 'Asistente' }
            ],
            seguros_sociales: {
              ccss: 'Al día',
              ins: 'Al día',
              ultima_cotizacion: '2024-06'
            }
          }
        });
      } else {
        setResult(data);
      }
    } catch (error) {
      setError('Error al buscar: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center mb-6">
        <span className="text-3xl mr-3">💼</span>
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Datos Laborales</h2>
          <p className="text-gray-600">Información laboral y historial de empleo</p>
        </div>
      </div>

      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-4">
          <input
            type="text"
            value={cedula}
            onChange={(e) => setCedula(e.target.value)}
            placeholder="Número de cédula (ej: 1-1234-5678)"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-cyan-600 hover:bg-cyan-700 text-white px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? '🔍 Consultando...' : '💼 Consultar Laboral'}
          </button>
        </div>
      </form>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          ❌ {error}
        </div>
      )}

      {result && (
        <div className="space-y-6">
          {result.found ? (
            <div>
              {/* Información básica de la persona */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <h3 className="text-lg font-semibold text-blue-800 mb-3">👤 Información Personal</h3>
                <div className="grid md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <div><strong>Nombre:</strong> {result.data.nombre}</div>
                    <div><strong>Apellidos:</strong> {result.data.primer_apellido} {result.data.segundo_apellido}</div>
                    <div><strong>Cédula:</strong> {result.data.cedula}</div>
                  </div>
                  <div>
                    <div><strong>Teléfono:</strong> {result.data.telefono || 'N/A'}</div>
                    <div><strong>Provincia:</strong> {result.data.provincia_nombre}</div>
                    <div><strong>Cantón:</strong> {result.data.canton_nombre}</div>
                  </div>
                </div>
              </div>

              {/* Datos laborales específicos */}
              {result.labor_data && (
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-purple-800 mb-3">💼 Información Laboral</h3>
                  
                  <div className="grid md:grid-cols-2 gap-6 mb-4">
                    <div>
                      <h4 className="font-medium text-purple-700 mb-2">Situación Actual:</h4>
                      <div className="space-y-1 text-sm">
                        <div><strong>Empleador:</strong> {result.labor_data.empleador_actual}</div>
                        <div><strong>Antigüedad:</strong> {result.labor_data.antiguedad}</div>
                        <div><strong>Tipo Contrato:</strong> {result.labor_data.tipo_contrato}</div>
                        <div><strong>Rango Salarial:</strong> {result.labor_data.salario_aproximado}</div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-purple-700 mb-2">Seguros Sociales:</h4>
                      <div className="space-y-1 text-sm">
                        <div><strong>CCSS:</strong> 
                          <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                            {result.labor_data.seguros_sociales.ccss}
                          </span>
                        </div>
                        <div><strong>INS:</strong> 
                          <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                            {result.labor_data.seguros_sociales.ins}
                          </span>
                        </div>
                        <div><strong>Última Cotización:</strong> {result.labor_data.seguros_sociales.ultima_cotizacion}</div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-purple-700 mb-2">Historial Laboral:</h4>
                    <div className="space-y-2">
                      {result.labor_data.historial_patronos.map((empleo, i) => (
                        <div key={i} className="bg-white border border-purple-100 rounded p-3">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-medium">{empleo.empresa}</div>
                              <div className="text-sm text-gray-600">{empleo.puesto}</div>
                            </div>
                            <div className="text-sm text-gray-500">{empleo.periodo}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded">
              ❌ No se encontraron datos laborales para: {cedula}
            </div>
          )}
        </div>
      )}

      <div className="mt-6 bg-gray-100 rounded-lg p-4">
        <h4 className="font-semibold text-gray-800 mb-2">🚧 Datos Laborales en Desarrollo</h4>
        <p className="text-gray-600 text-sm">
          Esta función está siendo integrada con datos del Ministerio de Trabajo y Seguridad Social.
          Pronto incluirá: historial completo de patronos, salarios exactos, liquidaciones laborales, y más.
        </p>
      </div>
    </div>
  );
};

// Componente para Estado Civil
const EstadoCivil = () => {
  const [cedula, setCedula] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!cedula.trim()) {
      setError('Por favor ingrese una cédula');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const data = await apiCall(`/search/cedula/${cedula}?enrich=true`);
      
      if (data.found) {
        // Simular datos de estado civil
        setResult({
          ...data,
          civil_data: {
            estado_civil: 'Casado(a)',
            fecha_matrimonio: '2018-06-15',
            regimen_matrimonial: 'Comunidad Absoluta de Bienes',
            conyugue: {
              nombre: 'María José',
              apellidos: 'González Vargas',
              cedula: '2-0456-0789'
            },
            divorcios_anteriores: 0,
            hijos_registrados: 2,
            lugar_matrimonio: 'San José, Costa Rica'
          }
        });
      } else {
        setResult(data);
      }
    } catch (error) {
      setError('Error al buscar: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center mb-6">
        <span className="text-3xl mr-3">💒</span>
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Estado Civil y Matrimonio</h2>
          <p className="text-gray-600">Información matrimonial y estado civil registral</p>
        </div>
      </div>

      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-4">
          <input
            type="text"
            value={cedula}
            onChange={(e) => setCedula(e.target.value)}
            placeholder="Número de cédula (ej: 1-1234-5678)"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-pink-600 hover:bg-pink-700 text-white px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? '🔍 Consultando...' : '💒 Consultar Estado Civil'}
          </button>
        </div>
      </form>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          ❌ {error}
        </div>
      )}

      {result && (
        <div className="space-y-6">
          {result.found ? (
            <div>
              {/* Información básica de la persona */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <h3 className="text-lg font-semibold text-blue-800 mb-3">👤 Información Personal</h3>
                <div className="grid md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <div><strong>Nombre:</strong> {result.data.nombre}</div>
                    <div><strong>Apellidos:</strong> {result.data.primer_apellido} {result.data.segundo_apellido}</div>
                    <div><strong>Cédula:</strong> {result.data.cedula}</div>
                  </div>
                  <div>
                    <div><strong>Teléfono:</strong> {result.data.telefono || 'N/A'}</div>
                    <div><strong>Provincia:</strong> {result.data.provincia_nombre}</div>
                    <div><strong>Cantón:</strong> {result.data.canton_nombre}</div>
                  </div>
                </div>
              </div>

              {/* Datos de estado civil */}
              {result.civil_data && (
                <div className="bg-pink-50 border border-pink-200 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-pink-800 mb-3">💒 Información Matrimonial</h3>
                  
                  <div className="grid md:grid-cols-2 gap-6 mb-4">
                    <div>
                      <h4 className="font-medium text-pink-700 mb-2">Estado Civil Actual:</h4>
                      <div className="space-y-1 text-sm">
                        <div><strong>Estado:</strong> 
                          <span className="ml-2 px-2 py-1 bg-pink-100 text-pink-800 rounded text-xs">
                            {result.civil_data.estado_civil}
                          </span>
                        </div>
                        <div><strong>Fecha Matrimonio:</strong> {result.civil_data.fecha_matrimonio}</div>
                        <div><strong>Lugar:</strong> {result.civil_data.lugar_matrimonio}</div>
                        <div><strong>Régimen:</strong> {result.civil_data.regimen_matrimonial}</div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-pink-700 mb-2">Información del Cónyuge:</h4>
                      <div className="space-y-1 text-sm">
                        <div><strong>Nombre:</strong> {result.civil_data.conyugue.nombre}</div>
                        <div><strong>Apellidos:</strong> {result.civil_data.conyugue.apellidos}</div>
                        <div><strong>Cédula:</strong> {result.civil_data.conyugue.cedula}</div>
                      </div>
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium text-pink-700 mb-2">Información Familiar:</h4>
                      <div className="space-y-1 text-sm">
                        <div><strong>Hijos Registrados:</strong> {result.civil_data.hijos_registrados}</div>
                        <div><strong>Divorcios Anteriores:</strong> {result.civil_data.divorcios_anteriores}</div>
                      </div>
                    </div>

                    <div className="flex items-center justify-center">
                      <div className="bg-white border-2 border-dashed border-pink-300 rounded-lg p-4 text-center">
                        <span className="text-4xl">💒</span>
                        <p className="text-xs text-pink-600 mt-2">Certificado de Matrimonio</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded">
              ❌ No se encontró información de estado civil para: {cedula}
            </div>
          )}
        </div>
      )}

      <div className="mt-6 bg-gray-100 rounded-lg p-4">
        <h4 className="font-semibold text-gray-800 mb-2">🚧 Datos de Estado Civil en Desarrollo</h4>
        <p className="text-gray-600 text-sm">
          Esta función está siendo integrada con datos del Registro Civil de Costa Rica.
          Pronto incluirá: certificados digitales, historial completo de matrimonios, información de hijos, y más.
        </p>
      </div>
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

// Navigation Bar Component con diseño mejorado
const NavigationBar = ({ activeSection, setActiveSection }) => {
  const { user, logout } = useAuth();
  const [activeDropdown, setActiveDropdown] = useState(null);

  const menuItems = [
    { 
      id: 'home', 
      label: 'Inicio', 
      icon: '🏠',
      description: 'Panel principal del sistema'
    },
    { 
      id: 'consultas-individuales', 
      label: 'Consultas Individuales', 
      icon: '👤',
      description: 'Búsquedas específicas por persona',
      submenu: [
        { id: 'foto', label: 'Consulta con Foto', icon: '📷', description: 'Búsqueda por cédula con foto incluida' },
        { id: 'cedula-global', label: 'Búsqueda Global', icon: '🌍', description: 'Búsqueda completa por cédula' },
        { id: 'telefono', label: 'Por Teléfono', icon: '📞', description: 'Búsqueda por número telefónico' },
        { id: 'nombres', label: 'Por Nombres', icon: '👥', description: 'Búsqueda por nombres y apellidos' }
      ]
    },
    { 
      id: 'consultas-masivas', 
      label: 'Consultas Masivas', 
      icon: '📊',
      description: 'Búsquedas en gran volumen',
      submenu: [
        { id: 'patronos', label: 'Patronos', icon: '🏢', description: 'Consulta masiva de patronos' },
        { id: 'geografica', label: 'Geográfica', icon: '🗺️', description: 'Búsqueda por ubicación geográfica' },
        { id: 'colegiados', label: 'Colegiados', icon: '🎓', description: 'Profesionales colegiados' },
        { id: 'pensionados', label: 'Pensionados', icon: '👴', description: 'Base de datos de pensionados' },
        { id: 'independientes', label: 'Independientes', icon: '💼', description: 'Trabajadores independientes' }
      ]
    },
    { 
      id: 'consultas-especiales', 
      label: 'Consultas Especiales', 
      icon: '⭐',
      description: 'Funciones especializadas',
      submenu: [
        { id: 'bloque-personales', label: 'Bloque Personales', icon: '🔒', description: 'Consultas en bloque de cédulas' },
        { id: 'mercantiles', label: 'Datos Mercantiles', icon: '🏬', description: 'Información comercial y mercantil' },
        { id: 'laborales', label: 'Datos Laborales', icon: '💼', description: 'Información laboral y empleos' },
        { id: 'matrimonio', label: 'Estado Civil', icon: '💒', description: 'Información matrimonial y civil' }
      ]
    },
    { 
      id: 'reportes', 
      label: 'Reportes y Estadísticas', 
      icon: '📈',
      description: 'Análisis y reportes del sistema',
      submenu: [
        { id: 'bitacora', label: 'Bitácora CSV', icon: '📋', description: 'Historial de consultas en CSV' },
        { id: 'estadisticas', label: 'Estadísticas', icon: '📊', description: 'Estadísticas del sistema' },
        { id: 'demograficos', label: 'Datos Demográficos', icon: '👥', description: 'Análisis demográfico' }
      ]
    },
    { 
      id: 'integraciones', 
      label: 'Integraciones', 
      icon: '🔗',
      description: 'Conexiones externas',
      submenu: [
        { id: 'telegram', label: 'Telegram Bot', icon: '📱', description: 'Integración con Telegram' },
        { id: 'sms-masivo', label: 'SMS Masivo', icon: '💬', description: 'Campañas de SMS masivo' },
        { id: 'exportar', label: 'Exportar Datos', icon: '📤', description: 'Exportar datos a diferentes formatos' }
      ]
    },
    { 
      id: 'admin', 
      label: 'Administración', 
      icon: '⚙️',
      description: 'Panel de administración del sistema'
    }
  ];

  const handleMenuClick = (item) => {
    if (item.submenu) {
      setActiveDropdown(activeDropdown === item.id ? null : item.id);
    } else {
      setActiveSection(item.id);
      setActiveDropdown(null);
    }
  };

  const handleSubmenuClick = (submenuItem) => {
    setActiveSection(submenuItem.id);
    setActiveDropdown(null);
  };

  return (
    <div className="bg-gradient-to-r from-indigo-900 via-blue-800 to-indigo-900 text-white shadow-2xl">
      {/* Header principal con logo y usuario */}
      <div className="bg-black bg-opacity-20 px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="bg-blue-600 rounded-full p-2">
              <h1 className="text-white text-xl font-bold tracking-wider">DATICOS v2.0</h1>
            </div>
            <div className="text-blue-200 text-sm">
              Sistema de Consultas y Análisis de Datos - Costa Rica
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-blue-200">👤 {user?.username || 'Usuario'}</span>
            <button
              onClick={logout}
              className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg text-sm transition-colors"
            >
              🚪 Salir
            </button>
          </div>
        </div>
      </div>

      {/* Menú de navegación principal */}
      <div className="px-6 py-2">
        <div className="flex flex-wrap gap-2">
          {menuItems.map((item) => (
            <div key={item.id} className="relative">
              <button
                onClick={() => handleMenuClick(item)}
                className={`
                  flex items-center space-x-2 px-4 py-3 rounded-lg transition-all duration-200 text-sm font-medium
                  ${activeSection === item.id || activeDropdown === item.id
                    ? 'bg-white bg-opacity-20 text-white shadow-lg'
                    : 'hover:bg-white hover:bg-opacity-10 text-blue-100 hover:text-white'
                  }
                `}
                title={item.description}
              >
                <span className="text-lg">{item.icon}</span>
                <span>{item.label}</span>
                {item.submenu && (
                  <span className={`transition-transform duration-200 ${
                    activeDropdown === item.id ? 'rotate-180' : ''
                  }`}>
                    ⌄
                  </span>
                )}
              </button>

              {/* Dropdown menu */}
              {item.submenu && activeDropdown === item.id && (
                <div className="absolute top-full left-0 mt-2 bg-white rounded-lg shadow-2xl border border-gray-200 min-w-64 z-50">
                  <div className="py-2">
                    <div className="px-4 py-2 border-b border-gray-100">
                      <h3 className="font-semibold text-gray-800 text-sm">{item.label}</h3>
                      <p className="text-gray-600 text-xs">{item.description}</p>
                    </div>
                    {item.submenu.map((submenuItem) => (
                      <button
                        key={submenuItem.id}
                        onClick={() => handleSubmenuClick(submenuItem)}
                        className={`
                          w-full text-left px-4 py-3 hover:bg-blue-50 transition-colors text-sm
                          ${activeSection === submenuItem.id ? 'bg-blue-100 text-blue-800' : 'text-gray-700'}
                        `}
                      >
                        <div className="flex items-center space-x-3">
                          <span className="text-lg">{submenuItem.icon}</span>
                          <div>
                            <div className="font-medium">{submenuItem.label}</div>
                            <div className="text-xs text-gray-500">{submenuItem.description}</div>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Breadcrumb */}
      {activeSection !== 'home' && (
        <div className="px-6 py-2 bg-black bg-opacity-10 text-blue-200 text-sm">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setActiveSection('home')}
              className="hover:text-white transition-colors"
            >
              🏠 Inicio
            </button>
            <span>›</span>
            <span className="text-white font-medium">
              {menuItems.find(item => item.id === activeSection)?.label || 
               menuItems.flatMap(item => item.submenu || []).find(sub => sub.id === activeSection)?.label ||
               'Sección Actual'}
            </span>
          </div>
        </div>
      )}
    </div>
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
    switch (activeSection) {
      case 'home':
        return <HomePage stats={stats} />;
      
      // Consultas Individuales con componentes específicos
      case 'foto':
        return <ConsultaFoto />;
        
      case 'cedula-global':
        return <BusquedaGlobal />;
        
      case 'telefono':
        return <BusquedaTelefono />;
        
      case 'nombres':
        return <BusquedaNombres />;
      
      // Consultas Masivas con componentes específicos
      case 'patronos':
        return <ConsultaPatronos />;
        
      case 'geografica':
        return <BusquedaGeograficaMasiva />;
        
      case 'colegiados':
        return <ConsultaMasivaTipo 
          tipo="colegiados" 
          titulo="Consulta Masiva de Colegiados"
          descripcion="Búsqueda de profesionales colegiados de Costa Rica"
          icono="🎓"
          color="bg-indigo-600 hover:bg-indigo-700"
        />;
        
      case 'pensionados':
        return <ConsultaMasivaTipo 
          tipo="pensionados" 
          titulo="Consulta Masiva de Pensionados"
          descripcion="Búsqueda de personas pensionadas por diferentes regímenes"
          icono="👴"
          color="bg-gray-600 hover:bg-gray-700"
        />;
        
      case 'independientes':
        return <ConsultaMasivaTipo 
          tipo="independientes" 
          titulo="Consulta Masiva de Independientes"
          descripcion="Trabajadores independientes y autónomos"
          icono="💼"
          color="bg-purple-600 hover:bg-purple-700"
        />;
      
      // Consultas Especiales 
      case 'bloque-personales':
        return <BloqueCedulas />;
        
      case 'mercantiles':
        return <DatosMercantiles />;
        
      case 'laborales':
        return <DatosLaborales />;
        
      case 'matrimonio':
        return <EstadoCivil />;
      
      // Reportes y Estadísticas
      case 'bitacora':
        return <BitacoraCSV />;
        
      case 'estadisticas':
        return <EstadisticasSistema />;
        
      case 'demograficos':
        return <DatosDemograficos />;
      
      // Integraciones
      case 'telegram':
        return <TelegramIntegration />;
        
      case 'sms-masivo':
        return <SMSMasivo />;
        
      case 'exportar':
        return <ExportarDatos />;
        
      // Administración
      case 'admin':
        return <AdminPanel />;
        
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



// Panel de Administración Completo
const AdminPanel = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [extractionTasks, setExtractionTasks] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (activeTab === 'dashboard') {
      loadDashboardStats();
    } else if (activeTab === 'extraction') {
      loadExtractionTasks();
    }
  }, [activeTab]);

  const loadDashboardStats = async () => {
    try {
      const data = await apiCall('/admin/dashboard/stats');
      setStats(data);
    } catch (error) {
      console.error('Error loading dashboard stats:', error);
    }
  };

  const loadExtractionTasks = async () => {
    try {
      const data = await apiCall('/admin/extraction/tasks');
      setExtractionTasks(data);
    } catch (error) {
      console.error('Error loading extraction tasks:', error);
    }
  };

  const testDaticosConnection = async () => {
    setLoading(true);
    try {
      const result = await apiCall('/admin/daticos/test-connection');
      setConnectionStatus(result);
    } catch (error) {
      console.error('Error testing connection:', error);
      setConnectionStatus({
        connection_status: 'error',
        message: 'Error en la prueba de conexión'
      });
    }
    setLoading(false);
  };

  const startExtraction = async () => {
    if (!window.confirm('¿Está seguro de iniciar la extracción masiva de datos de Daticos? Este proceso puede tomar varios minutos.')) {
      return;
    }

    setLoading(true);
    try {
      await apiCall('/admin/extraction/start', 'POST', {
        source: 'daticos_original',
        limit: 1000,
        extraction_type: 'full'
      });
      alert('Extracción iniciada exitosamente');
      loadExtractionTasks();
    } catch (error) {
      console.error('Error starting extraction:', error);
      alert('Error iniciando extracción: ' + error.message);
    }
    setLoading(false);
  };

  const cleanupDatabase = async () => {
    if (!window.confirm('¿Está seguro de limpiar registros duplicados? Esta acción no se puede deshacer.')) {
      return;
    }

    setLoading(true);
    try {
      const result = await apiCall('/admin/database/cleanup', 'POST');
      alert(`Limpieza completada: ${result.total_removed} registros eliminados`);
      loadDashboardStats();
    } catch (error) {
      console.error('Error cleaning database:', error);
      alert('Error en limpieza: ' + error.message);
    }
    setLoading(false);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
        ⚙️ <span className="ml-2">Panel de Administración</span>
      </h2>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex space-x-8">
          {[
            { id: 'dashboard', label: 'Dashboard', icon: '📊' },
            { id: 'extraction', label: 'Extracción de Datos', icon: '🔄' },
            { id: 'database', label: 'Gestión BD', icon: '💾' },
            { id: 'users', label: 'Usuarios', icon: '👥' },
            { id: 'settings', label: 'Configuración', icon: '⚙️' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-4 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && (
        <div className="space-y-6">
          {stats && (
            <>
              {/* System Statistics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-blue-100 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-blue-800">Personas Físicas</h3>
                  <p className="text-2xl font-bold text-blue-600">{stats.total_personas_fisicas?.toLocaleString()}</p>
                </div>
                
                <div className="bg-green-100 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-green-800">Personas Jurídicas</h3>
                  <p className="text-2xl font-bold text-green-600">{stats.total_personas_juridicas?.toLocaleString()}</p>
                </div>
                
                <div className="bg-purple-100 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-purple-800">Ubicaciones</h3>
                  <p className="text-2xl font-bold text-purple-600">
                    {(stats.total_provincias + stats.total_cantones + stats.total_distritos).toLocaleString()}
                  </p>
                </div>
                
                <div className="bg-orange-100 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-orange-800">Tamaño BD (MB)</h3>
                  <p className="text-2xl font-bold text-orange-600">{stats.database_size_mb}</p>
                </div>
              </div>

              {/* Data Sources Summary */}
              <div className="bg-gray-50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold text-gray-800 mb-4">📈 Fuentes de Datos</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {Object.entries(stats.data_sources_summary).map(([source, count]) => (
                    <div key={source} className="bg-white p-4 rounded-md">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-700 font-medium">{source.replace('_', ' ').toUpperCase()}</span>
                        <span className="text-xl font-bold text-gray-800">{count.toLocaleString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* Data Extraction Tab */}
      {activeTab === 'extraction' && (
        <div className="space-y-6">
          {/* Connection Test */}
          <div className="bg-blue-50 p-6 rounded-lg border-l-4 border-blue-500">
            <h3 className="text-lg font-semibold text-blue-800 mb-4">🔗 Prueba de Conexión con Daticos</h3>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={testDaticosConnection}
                disabled={loading}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Probando...' : 'Probar Conexión'}
              </button>
              
              {connectionStatus && (
                <div className={`px-4 py-2 rounded-md ${
                  connectionStatus.connection_status === 'success' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {connectionStatus.message}
                </div>
              )}
            </div>
          </div>

          {/* Extraction Controls */}
          <div className="bg-green-50 p-6 rounded-lg border-l-4 border-green-500">
            <h3 className="text-lg font-semibold text-green-800 mb-4">🚀 Extracción Masiva de Datos</h3>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={startExtraction}
                disabled={loading}
                className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 disabled:opacity-50"
              >
                {loading ? 'Iniciando...' : 'Iniciar Extracción'}
              </button>
              
              <span className="text-gray-600">
                Extraerá hasta 1,000 registros del sistema Daticos original
              </span>
            </div>
          </div>

          {/* Extraction Tasks List */}
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-4">📋 Historial de Extracciones</h3>
            
            {extractionTasks.length > 0 ? (
              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Tarea
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Estado
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Registros
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Progreso
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Fecha
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {extractionTasks.map((task) => (
                      <tr key={task.task_id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {task.task_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            task.status === 'completed' ? 'bg-green-100 text-green-800' :
                            task.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                            task.status === 'failed' ? 'bg-red-100 text-red-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {task.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {task.records_extracted}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {task.progress_percentage}%
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(task.created_at).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 bg-gray-50 rounded-lg">
                <p className="text-gray-600">No hay tareas de extracción registradas</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Database Management Tab */}
      {activeTab === 'database' && (
        <div className="space-y-6">
          <div className="bg-yellow-50 p-6 rounded-lg border-l-4 border-yellow-500">
            <h3 className="text-lg font-semibold text-yellow-800 mb-4">🧹 Limpieza de Base de Datos</h3>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={cleanupDatabase}
                disabled={loading}
                className="bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700 disabled:opacity-50"
              >
                {loading ? 'Limpiando...' : 'Eliminar Duplicados'}
              </button>
              
              <span className="text-gray-600">
                Removerá registros duplicados basados en número de cédula
              </span>
            </div>
          </div>

          <div className="bg-red-50 p-6 rounded-lg border-l-4 border-red-500">
            <h3 className="text-lg font-semibold text-red-800 mb-4">⚠️ Acciones Peligrosas</h3>
            
            <div className="space-y-4">
              <div>
                <button
                  className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
                  onClick={() => alert('Funcionalidad en desarrollo')}
                >
                  Resetear Base de Datos
                </button>
                <p className="text-sm text-red-700 mt-2">
                  Elimina todos los datos y reinicia la base de datos desde cero
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Users Tab */}
      {activeTab === 'users' && (
        <div className="space-y-6">
          <div className="bg-purple-50 p-6 rounded-lg border-l-4 border-purple-500">
            <h3 className="text-lg font-semibold text-purple-800 mb-4">👥 Gestión de Usuarios</h3>
            <p className="text-purple-700">Funcionalidad de gestión de usuarios en desarrollo</p>
          </div>
        </div>
      )}

      {/* Settings Tab */}
      {activeTab === 'settings' && (
        <div className="space-y-6">
          <div className="bg-gray-50 p-6 rounded-lg border-l-4 border-gray-500">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">⚙️ Configuración del Sistema</h3>
            <p className="text-gray-700">Configuraciones del sistema en desarrollo</p>
          </div>
        </div>
      )}
    </div>
  );
};

// Ayuda and Support Component (sin información de contacto de Daticos)
const AyudaSystem = () => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
        ❓ <span className="ml-2">Centro de Ayuda</span>
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Guía de Uso */}
        <div className="bg-blue-50 p-6 rounded-lg border-l-4 border-blue-500">
          <h3 className="text-xl font-bold text-blue-800 mb-4">📘 Guía de Uso</h3>
          
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold text-blue-700 mb-2">Consultas por Cédula</h4>
              <p className="text-gray-600 text-sm">
                Ingrese el número de cédula (física o jurídica) para obtener información detallada 
                de la persona o empresa registrada en el sistema.
              </p>
            </div>

            <div>
              <h4 className="font-semibold text-blue-700 mb-2">Búsquedas Geográficas</h4>
              <p className="text-gray-600 text-sm">
                Filtre resultados por provincia, cantón y distrito para encontrar personas 
                o empresas en ubicaciones específicas.
              </p>
            </div>

            <div>
              <h4 className="font-semibold text-blue-700 mb-2">Consultas por Nombre</h4>
              <p className="text-gray-600 text-sm">
                Busque personas físicas por nombre y apellidos, o empresas por nombre comercial 
                o razón social.
              </p>
            </div>

            <div>
              <h4 className="font-semibold text-blue-700 mb-2">Búsquedas por Teléfono</h4>
              <p className="text-gray-600 text-sm">
                Encuentre registros asociados a números telefónicos específicos.
                Soporta formatos con y sin guiones.
              </p>
            </div>
          </div>
        </div>

        {/* Preguntas Frecuentes */}
        <div className="bg-green-50 p-6 rounded-lg border-l-4 border-green-500">
          <h3 className="text-xl font-bold text-green-800 mb-4">❓ Preguntas Frecuentes</h3>
          
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold text-green-700 mb-2">¿Cómo buscar una empresa?</h4>
              <p className="text-gray-600 text-sm">
                Las empresas se buscan usando su cédula jurídica (formato 3-101-XXXXXX) 
                o su nombre comercial en la sección de búsqueda correspondiente.
              </p>
            </div>

            <div>
              <h4 className="font-semibold text-green-700 mb-2">¿Qué información se muestra?</h4>
              <p className="text-gray-600 text-sm">
                Para personas físicas: nombre, cédula, teléfono, dirección, ocupación.
                Para personas jurídicas: razón social, sector, representantes, ubicación.
              </p>
            </div>

            <div>
              <h4 className="font-semibold text-green-700 mb-2">¿Los datos se actualizan?</h4>
              <p className="text-gray-600 text-sm">
                Sí, el sistema se actualiza automáticamente con información de fuentes 
                oficiales y bases de datos verificadas.
              </p>
            </div>

            <div>
              <h4 className="font-semibold text-green-700 mb-2">¿Puedo exportar resultados?</h4>
              <p className="text-gray-600 text-sm">
                Los resultados pueden exportarse en formato CSV desde la opción 
                correspondiente en cada búsqueda.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Términos de Uso */}
      <div className="mt-8 bg-gray-50 p-6 rounded-lg">
        <h3 className="text-xl font-bold text-gray-800 mb-4">📋 Términos de Uso</h3>
        <div className="space-y-3 text-gray-600 text-sm">
          <p>• Los datos proporcionados provienen de fuentes públicas y oficiales de Costa Rica.</p>
          <p>• El uso de la información debe cumplir con la legislación vigente sobre protección de datos.</p>
          <p>• Este sistema está diseñado para consultas legítimas con fines comerciales, académicos o de investigación.</p>
          <p>• El usuario es responsable del uso que haga de la información obtenida.</p>
          <p>• Los datos se actualizan regularmente pero pueden no reflejar cambios recientes.</p>
        </div>
      </div>

      {/* Sistema de Soporte */}
      <div className="mt-8 bg-purple-50 p-6 rounded-lg border-l-4 border-purple-500">
        <h3 className="text-xl font-bold text-purple-800 mb-4">🛠️ Soporte Técnico</h3>
        <p className="text-gray-600 mb-4">
          Para asistencia técnica, consultas sobre funcionalidades o reportar problemas, 
          utilice las herramientas integradas en el panel de administración.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-md">
            <h4 className="font-semibold text-purple-700 mb-2">📊 Estado del Sistema</h4>
            <p className="text-gray-600 text-sm">Consulte el estado de servicios y bases de datos</p>
          </div>
          
          <div className="bg-white p-4 rounded-md">
            <h4 className="font-semibold text-purple-700 mb-2">📈 Estadísticas</h4>
            <p className="text-gray-600 text-sm">Vea métricas de uso y rendimiento del sistema</p>
          </div>
          
          <div className="bg-white p-4 rounded-md">
            <h4 className="font-semibold text-purple-700 mb-2">⚙️ Configuración</h4>
            <p className="text-gray-600 text-sm">Ajuste configuraciones desde el panel admin</p>
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
