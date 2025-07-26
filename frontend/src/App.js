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
        { id: 'patronos', label: 'Patronos' },
        { id: 'geografica', label: 'Geográfica' },
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
        { id: 'foto', label: 'Foto' },
        { id: 'global', label: 'Global' },
        { id: 'telefono', label: 'Telefono' },
        { id: 'nombres', label: 'Nombres' }
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
        const token = localStorage.getItem('daticos_token');
        const response = await axios.post(`${API}/demographics/query`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setStats(response.data);
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
      case 'patronos':
        return <PatronosSearch />;
      case 'geografica':
        return <GeograficaSearch />;
      case 'global':
        return <GlobalSearch />;
      case 'telefono':
        return <TelefonoSearch />;
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
            <p className="text-3xl font-bold text-blue-600">{stats.total_personas_fisicas.toLocaleString()}</p>
          </div>
          
          <div className="bg-green-100 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-green-800">Personas Jurídicas</h3>
            <p className="text-3xl font-bold text-green-600">{stats.total_personas_juridicas.toLocaleString()}</p>
          </div>
          
          <div className="bg-purple-100 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-purple-800">Provincias</h3>
            <p className="text-3xl font-bold text-purple-600">7</p>
          </div>
          
          <div className="bg-orange-100 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-orange-800">Total Registros</h3>
            <p className="text-3xl font-bold text-orange-600">
              {(stats.total_personas_fisicas + stats.total_personas_juridicas).toLocaleString()}
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
        <ul className="list-disc list-inside text-gray-600 space-y-2">
          <li>Consultas por ubicación geográfica</li>
          <li>Búsquedas individuales y masivas</li>
          <li>Estadísticas poblacionales</li>
          <li>Herramientas de prospectación</li>
          <li>Exportación de datos CSV</li>
        </ul>
      </div>
    </div>
  );
};

// Search Components
const PatronosSearch = () => {
  const [searchResults, setSearchResults] = useState([]);
  const [filters, setFilters] = useState({
    provincia_id: '',
    canton_id: '',
    distrito_id: ''
  });

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Búsqueda de Patronos</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <select className="px-4 py-2 border border-gray-300 rounded-md">
          <option value="">Seleccionar Provincia</option>
        </select>
        <select className="px-4 py-2 border border-gray-300 rounded-md">
          <option value="">Seleccionar Cantón</option>
        </select>
        <select className="px-4 py-2 border border-gray-300 rounded-md">
          <option value="">Seleccionar Distrito</option>
        </select>
      </div>
      <button className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700">
        Buscar
      </button>
    </div>
  );
};

const GeograficaSearch = () => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Consulta Geográfica</h2>
      <p className="text-gray-600">Búsquedas por ubicación geográfica específica.</p>
    </div>
  );
};

const GlobalSearch = () => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Consulta Global</h2>
      <p className="text-gray-600">Búsquedas masivas en toda la base de datos.</p>
    </div>
  );
};

const TelefonoSearch = () => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Búsqueda por Teléfono</h2>
      <p className="text-gray-600">Buscar por número telefónico.</p>
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
