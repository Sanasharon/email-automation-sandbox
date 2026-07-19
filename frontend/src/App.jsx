import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { MainLayout } from './layouts/MainLayout';
import { DashboardOverview } from './pages/DashboardOverview';
import { WorkflowControl } from './pages/WorkflowControl';
import { EmailMonitoring } from './pages/EmailMonitoring';
import { AutomationActivity } from './pages/AutomationActivity';
import { AuthProvider } from './context/AuthContext';
import { RefreshProvider } from './context/RefreshContext';
import { ProtectedRoute } from './context/ProtectedRoute';
import { ErrorBoundary } from './components/ErrorBoundary';

function App() {
  return (
    <AuthProvider>
      <RefreshProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={
              <ErrorBoundary>
                <ProtectedRoute>
                  <MainLayout />
                </ProtectedRoute>
              </ErrorBoundary>
            }>
              <Route index element={<ErrorBoundary><DashboardOverview /></ErrorBoundary>} />
              <Route path="workflows" element={<ErrorBoundary><WorkflowControl /></ErrorBoundary>} />
              <Route path="monitoring" element={<ErrorBoundary><EmailMonitoring /></ErrorBoundary>} />
              <Route path="automation" element={<ErrorBoundary><AutomationActivity /></ErrorBoundary>} />
              <Route path="automation/logs" element={<ErrorBoundary><div className="p-8"><h2>Full Logs (Placeholder)</h2></div></ErrorBoundary>} />
            </Route>
          </Routes>
        </BrowserRouter>
      </RefreshProvider>
    </AuthProvider>
  );
}

export default App;
