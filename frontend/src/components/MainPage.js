import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const MainPage = () => {
  const [stats, setStats] = useState({
    total_personas: 0,
    total_fotos: 0,
    total_telefonos: 0,
    total_emails: 0
  });
  
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/health`);
      const data = await response.json();
      
      if (data.database) {
        setStats({
          total_personas: data.database.personas_completas || 0,
          total_fotos: data.database.fotos_integradas || 0,
          total_telefonos: data.database.telefonos_registrados || 0,
          total_emails: data.database.emails_registrados || 0
        });
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching stats:', error);
      setLoading(false);
    }
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat('es-CR').format(num);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 text-white">
      {/* Header */}
      <header className="bg-black bg-opacity-30 backdrop-blur-lg border-b border-white border-opacity-10">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-xl flex items-center justify-center">
                <i className="fas fa-database text-2xl text-white"></i>
              </div>
              <div>
                <h1 className="text-4xl font-black bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
                  TuDatos
                </h1>
                <p className="text-lg text-blue-300">La Base de Datos Más Grande de Costa Rica</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <Link 
                to="/registro" 
                className="bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700 px-8 py-3 rounded-xl font-bold text-lg transition-all duration-300 transform hover:scale-105 shadow-xl"
              >
                <i className="fas fa-rocket mr-2"></i>
                Registrarse Ahora
              </Link>
              <Link 
                to="/login" 
                className="bg-white bg-opacity-10 hover:bg-opacity-20 px-6 py-3 rounded-xl font-bold border border-white border-opacity-20 transition-all duration-300"
              >
                Iniciar Sesión
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 text-center">
        <div className="max-w-7xl mx-auto px-6">
          <h1 className="text-7xl font-black mb-8 bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 bg-clip-text text-transparent">
            🚀 LA BASE DE DATOS MÁS GRANDE
            <br />DE COSTA RICA
          </h1>
          
          <p className="text-3xl mb-12 max-w-4xl mx-auto text-blue-200">
            <span className="font-black text-yellow-300">
              {loading ? 'Cargando...' : formatNumber(stats.total_personas)}
            </span> registros con datos ultra completos, fotos, WhatsApp verificado, 
            análisis crediticio y fusión inteligente de múltiples fuentes
          </p>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-16">
            <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl p-8 border border-white border-opacity-10">
              <div className="text-5xl font-black text-yellow-300 mb-4">
                {loading ? '⏳' : formatNumber(stats.total_personas)}
              </div>
              <div className="text-xl font-bold">Personas Registradas</div>
              <div className="text-blue-300">Datos completos verificados</div>
            </div>
            
            <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl p-8 border border-white border-opacity-10">
              <div className="text-5xl font-black text-green-300 mb-4">
                {loading ? '⏳' : formatNumber(stats.total_fotos)}
              </div>
              <div className="text-xl font-bold">Fotos Integradas</div>
              <div className="text-blue-300">Múltiples fuentes</div>
            </div>
            
            <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl p-8 border border-white border-opacity-10">
              <div className="text-5xl font-black text-blue-300 mb-4">
                {loading ? '⏳' : formatNumber(stats.total_telefonos)}
              </div>
              <div className="text-xl font-bold">Teléfonos</div>
              <div className="text-blue-300">WhatsApp verificado</div>
            </div>
            
            <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl p-8 border border-white border-opacity-10">
              <div className="text-5xl font-black text-purple-300 mb-4">
                {loading ? '⏳' : formatNumber(stats.total_emails)}
              </div>
              <div className="text-xl font-bold">Emails</div>
              <div className="text-blue-300">Verificados</div>
            </div>
          </div>

          <Link 
            to="/registro" 
            className="inline-block bg-gradient-to-r from-yellow-400 to-orange-500 hover:from-yellow-500 hover:to-orange-600 text-black px-12 py-6 rounded-2xl font-black text-2xl transition-all duration-300 transform hover:scale-105 shadow-2xl"
          >
            <i className="fas fa-star mr-3"></i>
            Acceder a 4.2M+ Registros
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-black bg-opacity-30">
        <div className="max-w-7xl mx-auto px-6">
          <h2 className="text-5xl font-black text-center mb-16 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            🌟 ¿Por Qué TuDatos es Único?
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            <div className="text-center group">
              <div className="w-32 h-32 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-8 group-hover:scale-110 transition-transform duration-300">
                <i className="fas fa-brain text-5xl text-white"></i>
              </div>
              <h3 className="text-2xl font-black mb-6 text-blue-300">Fusión Inteligente</h3>
              <p className="text-lg text-gray-300 leading-relaxed">
                Combina datos de múltiples fuentes gubernamentales y privadas 
                automáticamente para crear perfiles súper completos
              </p>
            </div>

            <div className="text-center group">
              <div className="w-32 h-32 bg-gradient-to-r from-green-500 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-8 group-hover:scale-110 transition-transform duration-300">
                <i className="fab fa-whatsapp text-5xl text-white"></i>
              </div>
              <h3 className="text-2xl font-black mb-6 text-green-300">WhatsApp Verificado</h3>
              <p className="text-lg text-gray-300 leading-relaxed">
                Verificación automática de números de WhatsApp en tiempo real 
                con datos de perfil y última actividad
              </p>
            </div>

            <div className="text-center group">
              <div className="w-32 h-32 bg-gradient-to-r from-yellow-500 to-red-600 rounded-full flex items-center justify-center mx-auto mb-8 group-hover:scale-110 transition-transform duration-300">
                <i className="fas fa-chart-line text-5xl text-white"></i>
              </div>
              <h3 className="text-2xl font-black mb-6 text-yellow-300">Análisis Crediticio</h3>
              <p className="text-lg text-gray-300 leading-relaxed">
                Score crediticio completo, análisis de riesgo, deudas estimadas 
                y capacidad de pago automática
              </p>
            </div>

            <div className="text-center group">
              <div className="w-32 h-32 bg-gradient-to-r from-purple-500 to-pink-600 rounded-full flex items-center justify-center mx-auto mb-8 group-hover:scale-110 transition-transform duration-300">
                <i className="fas fa-users text-5xl text-white"></i>
              </div>
              <h3 className="text-2xl font-black mb-6 text-purple-300">Datos Familiares</h3>
              <p className="text-lg text-gray-300 leading-relaxed">
                Información familiar completa del TSE: padres, hijos, cónyuge 
                y vínculos familiares verificados
              </p>
            </div>

            <div className="text-center group">
              <div className="w-32 h-32 bg-gradient-to-r from-indigo-500 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-8 group-hover:scale-110 transition-transform duration-300">
                <i className="fas fa-building text-5xl text-white"></i>
              </div>
              <h3 className="text-2xl font-black mb-6 text-indigo-300">Datos Laborales</h3>
              <p className="text-lg text-gray-300 leading-relaxed">
                Información laboral ultra detallada con salarios reales, 
                empresa actual e historial profesional
              </p>
            </div>

            <div className="text-center group">
              <div className="w-32 h-32 bg-gradient-to-r from-red-500 to-orange-600 rounded-full flex items-center justify-center mx-auto mb-8 group-hover:scale-110 transition-transform duration-300">
                <i className="fas fa-home text-5xl text-white"></i>
              </div>
              <h3 className="text-2xl font-black mb-6 text-red-300">Propiedades & Vehículos</h3>
              <p className="text-lg text-gray-300 leading-relaxed">
                Inmuebles registrados, vehículos con placas, avalúos 
                y datos del Registro Nacional
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto text-center px-6">
          <h2 className="text-6xl font-black mb-8 bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent">
            🎯 Sistema de Auto-Regeneración
          </h2>
          <p className="text-2xl mb-12 text-gray-300 leading-relaxed">
            Nuestro sistema mejora automáticamente cada día, agregando nuevos datos, 
            verificando información y optimizando la calidad. 
            <span className="font-bold text-yellow-300">¡Se hace más poderoso mientras duermes!</span>
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
            <div className="bg-gradient-to-r from-green-600 to-green-800 p-8 rounded-2xl">
              <h3 className="text-2xl font-bold mb-4">📈 Mejoras Diarias</h3>
              <p className="text-green-100">1,200+ registros mejorados cada 24 horas</p>
            </div>
            <div className="bg-gradient-to-r from-blue-600 to-blue-800 p-8 rounded-2xl">
              <h3 className="text-2xl font-bold mb-4">🎯 97.8% Precisión</h3>
              <p className="text-blue-100">Datos verificados con múltiples fuentes</p>
            </div>
          </div>

          <Link 
            to="/registro" 
            className="inline-block bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700 text-white px-12 py-6 rounded-2xl font-black text-2xl transition-all duration-300 transform hover:scale-105 shadow-2xl"
          >
            <i className="fas fa-rocket mr-3"></i>
            Comenzar Ahora
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-black bg-opacity-50 py-12">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <div className="flex items-center justify-center mb-6">
            <div className="w-12 h-12 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center mr-4">
              <i className="fas fa-database text-xl text-white"></i>
            </div>
            <h3 className="text-2xl font-black text-white">TuDatos</h3>
          </div>
          <p className="text-gray-400 mb-4">
            © 2025 TuDatos - La Base de Datos Más Grande de Costa Rica
          </p>
          <p className="text-gray-500 text-sm">
            Contacto empresarial: jykinternacional@gmail.com
          </p>
        </div>
      </footer>
    </div>
  );
};

export default MainPage;