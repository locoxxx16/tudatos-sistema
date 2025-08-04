import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const RegistrationPage = () => {
  const [creditPlans, setCreditPlans] = useState({});
  const [formData, setFormData] = useState({
    nombre_completo: '',
    email: '',
    telefono: '',
    empresa: '',
    plan_solicitado: '',
    motivo_uso: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);

  useEffect(() => {
    fetchCreditPlans();
  }, []);

  const fetchCreditPlans = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/credit-plans`);
      const data = await response.json();
      if (data.success) {
        setCreditPlans(data.plans);
      }
    } catch (error) {
      console.error('Error fetching credit plans:', error);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validar campos requeridos
    if (!formData.nombre_completo || !formData.email || !formData.telefono || !formData.plan_solicitado) {
      alert('⚠️ Por favor complete todos los campos requeridos');
      return;
    }
    
    setSubmitting(true);
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/register-request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const result = await response.json();
      
      if (result.success) {
        setShowSuccessModal(true);
      } else {
        alert('❌ ' + result.message);
      }
      
    } catch (error) {
      alert('❌ Error enviando solicitud. Intente nuevamente.');
    } finally {
      setSubmitting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      nombre_completo: '',
      email: '',
      telefono: '',
      empresa: '',
      plan_solicitado: '',
      motivo_uso: ''
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 text-white">
      {/* Header */}
      <header className="bg-black bg-opacity-30 backdrop-blur-lg border-b border-white border-opacity-10">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex justify-between items-center">
            <Link to="/" className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-xl flex items-center justify-center">
                <i className="fas fa-database text-xl text-white"></i>
              </div>
              <div>
                <h1 className="text-2xl font-black bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
                  TuDatos
                </h1>
                <p className="text-sm text-blue-300">La Base de Datos Más Grande de Costa Rica</p>
              </div>
            </Link>
            <Link 
              to="/" 
              className="bg-white bg-opacity-10 hover:bg-opacity-20 px-6 py-3 rounded-xl font-bold border border-white border-opacity-20 transition-all duration-300"
            >
              <i className="fas fa-home mr-2"></i>Volver al Inicio
            </Link>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="text-center mb-12">
          <h1 className="text-6xl font-black mb-6 bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 bg-clip-text text-transparent">
            🚀 REGISTRO EMPRESARIAL
          </h1>
          <p className="text-2xl text-gray-300 mb-8">
            Accede a la base de datos más completa de Costa Rica<br/>
            <span className="text-yellow-300 font-bold">4,283,709 registros</span> con fotos, datos familiares, laborales y bienes
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-12">
          {/* Formulario de Registro */}
          <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl p-8 border border-white border-opacity-10">
            <h2 className="text-3xl font-bold mb-8 text-center text-yellow-300">📋 Solicitud de Registro</h2>
            
            <form onSubmit={handleSubmit}>
              {/* Información Personal */}
              <div className="mb-6">
                <label className="block text-sm font-bold mb-2 text-yellow-300">
                  <i className="fas fa-user mr-2"></i>Nombre Completo *
                </label>
                <input 
                  type="text" 
                  name="nombre_completo"
                  value={formData.nombre_completo}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-400" 
                  placeholder="Ej: Juan Carlos Rodríguez Pérez" 
                  required 
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <label className="block text-sm font-bold mb-2 text-yellow-300">
                    <i className="fas fa-envelope mr-2"></i>Email Corporativo *
                  </label>
                  <input 
                    type="email" 
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-400" 
                    placeholder="correo@empresa.com" 
                    required 
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold mb-2 text-yellow-300">
                    <i className="fas fa-phone mr-2"></i>Teléfono *
                  </label>
                  <input 
                    type="tel" 
                    name="telefono"
                    value={formData.telefono}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-400" 
                    placeholder="+506 8888-8888" 
                    required 
                  />
                </div>
              </div>

              {/* Información Empresarial */}
              <div className="mb-6">
                <label className="block text-sm font-bold mb-2 text-yellow-300">
                  <i className="fas fa-building mr-2"></i>Empresa
                </label>
                <input 
                  type="text" 
                  name="empresa"
                  value={formData.empresa}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-400" 
                  placeholder="Nombre de su empresa" 
                />
              </div>

              {/* Plan Seleccionado */}
              <div className="mb-6">
                <label className="block text-sm font-bold mb-2 text-yellow-300">
                  <i className="fas fa-star mr-2"></i>Plan Solicitado *
                </label>
                <select 
                  name="plan_solicitado"
                  value={formData.plan_solicitado}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-400" 
                  required
                >
                  <option value="">Seleccione un plan...</option>
                  {Object.entries(creditPlans).map(([key, plan]) => (
                    <option key={key} value={key} className="bg-gray-800">
                      {plan.nombre} - {plan.creditos} consultas (${plan.precio_usd} USD)
                    </option>
                  ))}
                </select>
              </div>

              {/* Motivo de Uso */}
              <div className="mb-8">
                <label className="block text-sm font-bold mb-2 text-yellow-300">
                  <i className="fas fa-clipboard mr-2"></i>Motivo de Uso
                </label>
                <textarea 
                  name="motivo_uso"
                  value={formData.motivo_uso}
                  onChange={handleInputChange}
                  rows="4"
                  className="w-full px-4 py-3 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-400" 
                  placeholder="Describa brevemente para qué utilizará la plataforma..."
                ></textarea>
              </div>

              <button 
                type="submit" 
                disabled={submitting}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 py-4 rounded-xl font-bold text-xl transition-all disabled:opacity-50 transform hover:scale-105 shadow-xl"
              >
                <i className={`mr-3 ${submitting ? 'fas fa-spinner fa-spin' : 'fas fa-paper-plane'}`}></i>
                {submitting ? 'Enviando solicitud...' : 'Solicitar Acceso'}
              </button>
            </form>

            <div className="text-center mt-6 text-gray-400">
              <p className="text-sm">
                <i className="fas fa-shield-alt mr-2 text-green-400"></i>
                Su solicitud será revisada por nuestro equipo.<br/>
                Nos contactaremos con usted en 24-48 horas.
              </p>
            </div>
          </div>

          {/* Planes Detallados */}
          <div className="space-y-6">
            <h2 className="text-3xl font-bold text-center mb-8 text-yellow-300">💎 Planes Disponibles</h2>
            
            {Object.entries(creditPlans).map(([key, plan]) => {
              const borderColor = key === 'basico' ? 'border-blue-400' : 
                                key === 'profesional' ? 'border-green-400' : 
                                key === 'premium' ? 'border-yellow-400' : 'border-purple-400';
              const textColor = key === 'basico' ? 'text-blue-300' : 
                              key === 'profesional' ? 'text-green-300' : 
                              key === 'premium' ? 'text-yellow-300' : 'text-purple-300';
              
              return (
                <div key={key} className={`bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-6 border-2 ${borderColor} ${key === 'premium' ? 'relative' : ''}`}>
                  {key === 'premium' && (
                    <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                      <span className="bg-yellow-400 text-black px-4 py-1 rounded-full font-bold text-sm">MÁS POPULAR</span>
                    </div>
                  )}
                  <div className="flex justify-between items-start mb-4">
                    <h3 className={`text-2xl font-bold ${textColor}`}>{plan.nombre}</h3>
                    <div className="text-right">
                      <div className="text-3xl font-black">${plan.precio_usd} USD</div>
                      <div className="text-sm text-gray-400">{plan.creditos.toLocaleString()} consultas</div>
                    </div>
                  </div>
                  <p className="text-gray-300 mb-4">{plan.descripcion}</p>
                  
                  {/* Features específicas por plan */}
                  <ul className="space-y-2 text-sm">
                    <li><i className="fas fa-check text-green-400 mr-2"></i>Búsqueda por nombre y cédula</li>
                    <li><i className="fas fa-check text-green-400 mr-2"></i>Información de contacto verificada</li>
                    <li><i className="fas fa-check text-green-400 mr-2"></i>Datos familiares básicos</li>
                    
                    {(key === 'profesional' || key === 'premium' || key === 'corporativo') && (
                      <>
                        <li><i className="fas fa-check text-green-400 mr-2"></i>Fotos de perfil y cédula</li>
                        <li><i className="fas fa-check text-green-400 mr-2"></i>Información laboral detallada</li>
                        <li><i className="fas fa-check text-green-400 mr-2"></i>Datos de propiedades</li>
                      </>
                    )}
                    
                    {(key === 'premium' || key === 'corporativo') && (
                      <>
                        <li><i className="fas fa-check text-green-400 mr-2"></i>Verificación WhatsApp automática</li>
                        <li><i className="fas fa-check text-green-400 mr-2"></i>Análisis crediticio completo</li>
                        <li><i className="fas fa-check text-green-400 mr-2"></i>Redes sociales integradas</li>
                        <li><i className="fas fa-check text-green-400 mr-2"></i>Datos de vehículos</li>
                      </>
                    )}
                    
                    {key === 'corporativo' && (
                      <>
                        <li><i className="fas fa-check text-green-400 mr-2"></i>API dedicada para integración</li>
                        <li><i className="fas fa-check text-green-400 mr-2"></i>Exportación de datos masiva</li>
                        <li><i className="fas fa-check text-green-400 mr-2"></i>Soporte técnico 24/7</li>
                        <li><i className="fas fa-check text-green-400 mr-2"></i>Manager de cuenta dedicado</li>
                      </>
                    )}
                  </ul>
                </div>
              );
            })}
          </div>
        </div>

        {/* Características Únicas */}
        <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl p-8 border border-white border-opacity-10 text-center">
          <h2 className="text-4xl font-bold mb-8 text-yellow-300">🌟 ¿Por Qué TuDatos es Único?</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <i className="fas fa-database text-5xl text-blue-400 mb-4"></i>
              <h3 className="text-xl font-bold mb-3">Base de Datos Masiva</h3>
              <p className="text-gray-300">4.2+ millones de registros fusionados inteligentemente de múltiples fuentes oficiales</p>
            </div>
            <div>
              <i className="fas fa-shield-check text-5xl text-green-400 mb-4"></i>
              <h3 className="text-xl font-bold mb-3">Datos Verificados</h3>
              <p className="text-gray-300">Información verificada en tiempo real con múltiples fuentes gubernamentales y privadas</p>
            </div>
            <div>
              <i className="fas fa-lightning-bolt text-5xl text-yellow-400 mb-4"></i>
              <h3 className="text-xl font-bold mb-3">Búsqueda Ultra Rápida</h3>
              <p className="text-gray-300">Resultados instantáneos con fusión inteligente y análisis automático</p>
            </div>
          </div>
        </div>
      </div>

      {/* Modal Éxito */}
      {showSuccessModal && (
        <div className="fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center p-4">
          <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl max-w-lg w-full p-8 text-center border border-white border-opacity-20">
            <i className="fas fa-check-circle text-6xl text-green-400 mb-6"></i>
            <h2 className="text-3xl font-bold mb-4">¡Solicitud Enviada!</h2>
            <p className="text-lg text-gray-300 mb-6">
              Su solicitud ha sido enviada exitosamente a <strong className="text-yellow-300">jykinternacional@gmail.com</strong>
            </p>
            <p className="text-sm text-gray-400 mb-8">
              Nos pondremos en contacto con usted en las próximas 24-48 horas para activar su cuenta.
            </p>
            <button 
              onClick={() => {setShowSuccessModal(false); resetForm();}}
              className="bg-green-600 hover:bg-green-700 px-8 py-3 rounded-xl font-bold text-lg transition-all duration-300 transform hover:scale-105"
            >
              <i className="fas fa-home mr-2"></i>Entendido
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default RegistrationPage;