import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const SuperpowersPage = () => {
  const navigate = useNavigate();
  const [superpowers, setSuperpowers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const handleSuperpowerClick = (superpowerKey) => {
    console.log(`🎯 Navigating to /${superpowerKey}`);
    navigate(`/${superpowerKey}`);
  };

  useEffect(() => {
    const fetchSuperpowers = async () => {
      try {
        console.log('🚀 Starting fetch to /api/superpowers...');
        
        const response = await fetch('https://100.83.147.76:8003/api/superpowers');
        console.log('📡 Response received:', {
          status: response.status,
          statusText: response.statusText,
          ok: response.ok,
          url: response.url
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('❌ HTTP Error:', response.status, response.statusText);
          console.error('❌ Error response body:', errorText);
          throw new Error(`HTTP ${response.status}: ${response.statusText} - ${errorText}`);
        }
        
        // Get the raw response text first to see what we're actually getting
        const responseText = await response.text();
        console.log('📝 Raw response text:', responseText);
        console.log('📝 Response text length:', responseText.length);
        console.log('📝 Response text type:', typeof responseText);
        
        // Try to parse as JSON
        let data;
        try {
          data = JSON.parse(responseText);
          console.log('✅ Data parsed successfully:', data);
        } catch (parseError) {
          console.error('💥 JSON Parse Error:', parseError);
          console.error('💥 Failed to parse this text as JSON:', responseText);
          throw new Error(`Invalid JSON response: ${parseError.message}`);
        }
        console.log('📊 Superpowers found:', data.superpowers?.length || 0);
        
        if (!data.superpowers) {
          console.warn('⚠️ No superpowers array in response');
          setSuperpowers([]);
        } else {
          setSuperpowers(data.superpowers);
          console.log('✅ Superpowers set in state');
        }
        
      } catch (err) {
        console.error('💥 Fetch error occurred:', err);
        console.error('💥 Error type:', err.constructor.name);
        console.error('💥 Error message:', err.message);
        console.error('💥 Full error object:', err);
        setError(`${err.name}: ${err.message}`);
      } finally {
        console.log('🏁 Fetch completed, setting loading to false');
        setLoading(false);
      }
    };

    fetchSuperpowers();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="bg-white/20 backdrop-blur-lg rounded-2xl p-6 border border-white/30">
          <div className="text-red-600 font-medium">
            <p>Failed to load superpowers</p>
            <p className="text-sm mt-2 opacity-80">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 relative overflow-hidden">
      {/* Background blur elements */}
      <div className="absolute top-20 left-10 w-72 h-72 bg-blue-200/30 rounded-full blur-3xl"></div>
      <div className="absolute bottom-20 right-10 w-80 h-80 bg-purple-200/30 rounded-full blur-3xl"></div>
      <div className="absolute top-1/2 left-1/3 w-64 h-64 bg-indigo-200/20 rounded-full blur-3xl"></div>
      
      {/* Content */}
      <div className="relative z-10 px-6 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-10">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Superpowers</h1>
            <p className="text-gray-600">Discover your available capabilities</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {superpowers.map((power) => (
              <div
                key={power.key}
                onClick={() => handleSuperpowerClick(power.key)}
                className="bg-white/20 backdrop-blur-lg rounded-3xl p-6 border border-white/30 shadow-lg hover:shadow-xl transition-all duration-300 hover:bg-white/25 hover:scale-[1.02] cursor-pointer active:scale-[0.98]"
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold text-gray-900">{power.name}</h3>
                  <div className="w-3 h-3 bg-green-400 rounded-full shadow-sm"></div>
                </div>
                
                <div className="space-y-3">
                  {Object.entries(power.intents).map(([key, description], index) => (
                    <div key={key} className="flex items-start space-x-3">
                      <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2 flex-shrink-0"></div>
                      <div>
                        <p className="text-sm font-medium text-gray-800 capitalize">{key.replace('_', ' ')}</p>
                        <p className="text-xs text-gray-600 leading-relaxed">{description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {superpowers.length === 0 && (
            <div className="text-center py-12">
              <div className="bg-white/20 backdrop-blur-lg rounded-2xl p-8 border border-white/30 inline-block">
                <p className="text-gray-600">No superpowers available</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SuperpowersPage;