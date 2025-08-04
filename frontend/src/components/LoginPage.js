import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const LoginPage = () => {
  const [loginData, setLoginData] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    setLoginData({
      ...loginData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginData)
      });

      const result = await response.json();

      if (result.success) {
        // Guardar token en localStorage
        localStorage.setItem('token', result.token);
        localStorage.setItem('user', JSON.stringify(result.admin));
        
        // Redirigir al dashboard correspondiente
        if (result.admin.role === 'admin') {
          navigate('/admin/dashboard');
        } else {
          navigate('/user/dashboard');
        }
      } else {
        alert('❌ Credenciales incorrectas');
      }
    } catch (error) {
      alert('❌ Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 text-white flex items-center justify-center">
      <div className="max-w-md w-full mx-4">
        {/* Header */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center justify-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-xl flex items-center justify-center mr-4">
              <i className="fas fa-database text-2xl text-white"></i>
            </div>
            <div className="text-left">
              <h1 className="text-3xl font-black bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
                TuDatos
              </h1>
              <p className="text-sm text-blue-300">Base de Datos de Costa Rica</p>
            </div>
          </Link>
          
          <h2 className="text-4xl font-bold mb-4">Iniciar Sesión</h2>
          <p className="text-gray-400">Accede a tu panel de control</p>
        </div>

        {/* Login Form */}
        <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl p-8 border border-white border-opacity-10">
          <form onSubmit={handleSubmit}>
            <div className="mb-6">
              <label className="block text-sm font-bold mb-2 text-yellow-300">
                <i className="fas fa-user mr-2"></i>Usuario
              </label>
              <input
                type="text"
                name="username"
                value={loginData.username}
                onChange={handleInputChange}
                className="w-full px-4 py-3 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-400"
                placeholder="Ingrese su usuario"
                required
              />
            </div>

            <div className="mb-8">
              <label className="block text-sm font-bold mb-2 text-yellow-300">
                <i className="fas fa-lock mr-2"></i>Contraseña
              </label>
              <input
                type="password"
                name="password"
                value={loginData.password}
                onChange={handleInputChange}
                className="w-full px-4 py-3 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-400"
                placeholder="Ingrese su contraseña"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 py-4 rounded-xl font-bold text-xl transition-all disabled:opacity-50 transform hover:scale-105 shadow-xl"
            >
              <i className={`mr-3 ${loading ? 'fas fa-spinner fa-spin' : 'fas fa-sign-in-alt'}`}></i>
              {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-400 text-sm">
              ¿No tienes cuenta? <Link to="/registro" className="text-yellow-300 hover:text-yellow-200 font-bold">Regístrate aquí</Link>
            </p>
          </div>
        </div>

        {/* Back to Home */}
        <div className="text-center mt-8">
          <Link 
            to="/" 
            className="inline-flex items-center text-blue-300 hover:text-blue-200 transition-colors"
          >
            <i className="fas fa-arrow-left mr-2"></i>
            Volver al Inicio
          </Link>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;