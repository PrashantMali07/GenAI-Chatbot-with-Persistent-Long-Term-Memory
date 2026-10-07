import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import api from '../lib/api';
import { BrainCircuit, Loader2 } from 'lucide-react';

export default function Login() {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      let token = '';
      if (isLogin) {
        // Use application/x-www-form-urlencoded for OAuth2 login
        const params = new URLSearchParams();
        params.append('username', username);
        params.append('password', password);
        
        const res = await api.post('/api/auth/login', params, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        token = res.data.access_token;
      } else {
        const res = await api.post('/api/auth/register', { username, password });
        token = res.data.access_token;
      }

      // Fetch user profile to get userId and username
      const meRes = await api.get('/api/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setAuth(token, meRes.data.user_id, meRes.data.username);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center items-center p-4">
      <div className="w-full max-w-md bg-card border rounded-xl shadow-sm p-8">
        <div className="flex flex-col items-center mb-8">
          <div className="p-3 bg-primary/10 rounded-full mb-4">
            <BrainCircuit className="w-10 h-10 text-primary" />
          </div>
          <h1 className="text-2xl font-bold text-card-foreground">
            {isLogin ? 'Welcome back' : 'Create an account'}
          </h1>
          <p className="text-muted-foreground text-sm mt-2">
            GenAI Chatbot with Long-Term Memory
          </p>
        </div>

        {error && (
          <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md mb-6">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Username</label>
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full p-2 border rounded-md bg-background focus:ring-2 focus:ring-primary focus:outline-none"
              placeholder="Enter your username"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-2 border rounded-md bg-background focus:ring-2 focus:ring-primary focus:outline-none"
              placeholder="••••••••"
            />
          </div>
          
          <button
            type="submit"
            disabled={loading || !username || !password}
            className="w-full bg-primary text-primary-foreground p-2 rounded-md font-medium hover:bg-primary/90 flex justify-center items-center disabled:opacity-50 transition-colors"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (isLogin ? 'Sign In' : 'Sign Up')}
          </button>
        </form>

        <div className="mt-6 text-center text-sm">
          <button
            onClick={() => { setIsLogin(!isLogin); setError(''); }}
            className="text-primary hover:underline"
          >
            {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
          </button>
        </div>
      </div>
    </div>
  );
}
