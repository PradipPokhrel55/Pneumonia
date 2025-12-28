import React, { useContext } from "react";
import { Navigate } from "react-router-dom";
import AuthContext from "./assets/Auth/AuthContext.jsx";

const ProtectedRoute = ({ children }) => {
  const { user } = useContext(AuthContext);
  if (!user) return <Navigate to="/" />; 
  return children;
};

export default ProtectedRoute;
