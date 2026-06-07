import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout.jsx';
import Dashboard from './pages/Dashboard.jsx';
import QueryPage from './pages/QueryPage.jsx';
import EvaluationPage from './pages/EvaluationPage.jsx';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/query" element={<QueryPage />} />
          <Route path="/evaluation" element={<EvaluationPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
