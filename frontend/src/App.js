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

// Search by Cedula Component
const CedulaSearch = () => {
  const [cedula, setCedula] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!cedula.trim()) return;

    setLoading(true);
    try {
      const data = await apiCall(`/search/cedula/${cedula}`);
      setResult(data);
    } catch (error) {
      console.error('Error searching by cedula:', error);
      setResult({ found: false, message: 'Error en la búsqueda' });
    }
    setLoading(false);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Búsqueda por Cédula</h2>
      
      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-4">
          <input
            type="text"
            placeholder="Ingrese número de cédula (ej: 123456789 o 3-101-123456)"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={cedula}
            onChange={(e) => setCedula(e.target.value)}
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-8 py-3 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Buscando...' : 'Buscar'}
          </button>
        </div>
      </form>

      {result && (
        <div className="mt-6">
          {result.found ? (
            <ResultsTable results={[result]} loading={false} />
          ) : (
            <div className="bg-yellow-100 border border-yellow-400 text-yellow-800 px-4 py-3 rounded">
              {result.message}
            </div>
          )}
        </div>
      )}
    </div>
  );
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
    switch (activeSection) {
      case 'home':
        return <HomePage stats={stats} />;
      case 'cedula':
        return <CedulaSearch />;
      case 'geografica':
        return <GeograficaSearch />;
      case 'nombres':
        return <NombresSearch />;
      case 'telefono':
        return <TelefonoSearch />;
      case 'global':
        return <GlobalSearch />;
      case 'patronos':
        return <PatronosSearch />;
      default:
        return <HomePage stats={stats} />;
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

// Additional Search Components
const GlobalSearch = () => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Consulta Global</h2>
      <div className="text-center py-12 text-gray-500">
        <p className="text-xl mb-4">🔍</p>
        <p>Función de búsqueda global en desarrollo</p>
        <p className="text-sm">Esta función permitirá realizar consultas masivas en toda la base de datos.</p>
      </div>
    </div>
  );
};

const PatronosSearch = () => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Búsqueda de Patronos</h2>
      <div className="text-center py-12 text-gray-500">
        <p className="text-xl mb-4">🏭</p>
        <p>Búsqueda de patronos y empleadores</p>
        <p className="text-sm">Esta función mostrará información de empresas registradas como patronos.</p>
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
