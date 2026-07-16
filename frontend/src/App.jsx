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

function App() {
  return (
    <AuthProvider>
      <RefreshProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }>
              <Route index element={<DashboardOverview />} />
          <Route path="workflows" element={<WorkflowControl />} />
          <Route path="monitoring" element={<EmailMonitoring />} />
          <Route path="automation" element={<AutomationActivity />} />
              <Route path="automation/logs" element={<div className="p-8"><h2>Full Logs (Placeholder)</h2></div>} />
            </Route>
          </Routes>
        </BrowserRouter>
      </RefreshProvider>
    </AuthProvider>
  );
}

export default App;
