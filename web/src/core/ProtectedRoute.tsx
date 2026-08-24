import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';

interface ProtectedRouteProps {
  allowedRoles: Array<'student' | 'teacher' | 'admin'>;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ allowedRoles }) => {
  const token = localStorage.getItem('cipherpage_token');
  const userRole = localStorage.getItem('cipherpage_user_role') as 'student' | 'teacher' | 'admin' | null;
  const location = useLocation();

  if (!token) {
    // Redirect unauthenticated users back to login, saving their intent
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (userRole && !allowedRoles.includes(userRole)) {
    // Role-Based Access Control (RBAC): Redirect unauthorized roles
    const redirectPath = userRole === 'admin' ? '/admin/dashboard' : '/portal';
    return <Navigate to={redirectPath} replace />;
  }

  // If authenticated and authorized, render the child routes
  return <Outlet />;
};
