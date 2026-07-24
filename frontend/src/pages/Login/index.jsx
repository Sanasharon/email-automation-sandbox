import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Mail, Lock, ArrowRight, Activity, ShieldCheck } from 'lucide-react';

export const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const from = location.state?.from?.pathname || '/';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    
    try {
      const result = await login(email, password);
      if (result.success) {
        navigate(from, { replace: true });
      } else {
        setError(result.error || 'Failed to login');
      }
    } catch (err) {
      setError('An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Left side - branding */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-between bg-blue-700 p-12 text-white">
        <div>
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-white/20 p-2 backdrop-blur-sm">
              <Activity className="h-8 w-8 text-white" />
            </div>
            <span className="text-2xl font-bold tracking-tight">Utservio</span>
          </div>
          <div className="mt-16 max-w-lg">
            <h1 className="text-4xl font-bold leading-tight text-white mb-6">
              Email Automation Engine
            </h1>
            <p className="text-lg text-blue-100">
              Securely monitor, manage, and automate your organization's email workflows. 
              Built for scale and performance.
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-4 text-blue-200">
          <ShieldCheck className="h-6 w-6" />
          <span className="text-sm font-medium">Enterprise Grade Security Enabled</span>
        </div>
      </div>

      {/* Right side - login form */}
      <div className="flex w-full lg:w-1/2 flex-col justify-center px-8 sm:px-16 md:px-24 xl:px-32">
        <div className="mb-10 text-center lg:hidden">
          <div className="inline-flex items-center justify-center rounded-xl bg-blue-100 p-3 dark:bg-blue-900/30">
            <Activity className="h-8 w-8 text-blue-600 dark:text-blue-400" />
          </div>
          <h2 className="mt-4 text-2xl font-bold text-gray-900 dark:text-white">Utservio Dashboard</h2>
        </div>

        <div className="mb-10">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">Welcome back</h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Please sign in to access your automation dashboard.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="rounded-lg bg-red-50 p-4 border border-red-200 dark:bg-red-900/30 dark:border-red-800">
              <div className="flex items-center gap-3">
                <div className="text-sm text-red-700 dark:text-red-400 font-medium">{error}</div>
              </div>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Email Address
              </label>
              <div className="relative">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <Mail className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full rounded-xl border border-gray-300 bg-white p-3 pl-10 text-sm shadow-sm transition-all focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white dark:focus:border-blue-500"
                  placeholder="Enter your email"
                  required
                />
              </div>
            </div>

            <div>
              <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Password
              </label>
              <div className="relative">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full rounded-xl border border-gray-300 bg-white p-3 pl-10 text-sm shadow-sm transition-all focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white dark:focus:border-blue-500"
                  placeholder="Enter your password"
                  required
                />
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800"
              />
              <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                Remember me
              </label>
            </div>

            <div className="text-sm">
              <span className="font-medium text-gray-400 dark:text-gray-600 cursor-not-allowed">
                Forgot password?
              </span>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="group flex w-full items-center justify-center rounded-xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white shadow-sm transition-all hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-70 dark:focus:ring-offset-gray-900"
          >
            {isLoading ? (
              <div className="flex items-center gap-2">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                Signing in...
              </div>
            ) : (
              <div className="flex items-center gap-2">
                Sign in
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </div>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
