import React, { createContext, useState, useEffect } from "react";
import { jwtDecode } from "jwt-decode"; // ✅ Correct import for named export
import { useNavigate } from "react-router-dom";

const AuthContext = createContext();
export default AuthContext;

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const AuthProvider = ({ children }) => {
  const [authTokens, setAuthTokens] = useState(() => {
    try {
      const tokens = localStorage.getItem("authTokens");
      return tokens ? JSON.parse(tokens) : null;
    } catch (err) {
      console.error("Failed to parse tokens from localStorage:", err);
      return null;
    }
  });

  const [user, setUser] = useState(() => {
    try {
      return authTokens?.access ? jwtDecode(authTokens.access) : null;
    } catch (err) {
      console.error("Invalid token on init:", err);
      return null;
    }
  });

  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const safeDecode = (token) => {
    try {
      return jwtDecode(token);
    } catch (err) {
      console.error("Failed to decode token:", err);
      return null;
    }
  };

  const loginUser = async (username, password) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/token/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        alert("Login failed! Check credentials.");
        return;
      }

      const data = await response.json();
      if (data.access && data.refresh) {
        setAuthTokens(data);
        setUser(safeDecode(data.access));
        localStorage.setItem("authTokens", JSON.stringify(data));
        navigate("/chat");
      } else {
        alert("Login failed! Missing tokens.");
      }
    } catch (err) {
      console.error("Login error:", err);
      alert("Login failed! Try again.");
    }
  };

  const logoutUser = () => {
    setAuthTokens(null);
    setUser(null);
    localStorage.removeItem("authTokens");
    navigate("/");
  };

  const updateToken = async () => {
    if (!authTokens?.refresh) {
      console.warn("No refresh token found, logging out...");
      logoutUser();
      setLoading(false); // Reset loading state
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/token/refresh/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh: authTokens.refresh }),
      });

      if (!response.ok) {
        console.warn("Refresh failed, logging out...");
        logoutUser();
        return;
      }

      const data = await response.json();
      if (data.access) {
        const decodedUser = safeDecode(data.access);
        if (!decodedUser) {
          logoutUser();
          return;
        }
        setAuthTokens(data);
        setUser(decodedUser);
        localStorage.setItem("authTokens", JSON.stringify(data));
      } else {
        logoutUser();
      }
    } catch (err) {
      console.error("Token refresh error:", err);
      logoutUser();
    } finally {
      setLoading(false); // ✅ Always reset loading
    }
  };

  useEffect(() => {
    if (loading) {
      updateToken();
    }
    const interval = setInterval(() => {
      if (authTokens) updateToken();
    }, 1000 * 60 * 4); // every 4 mins

    return () => clearInterval(interval);
  }, [authTokens, loading]);

  return (
    <AuthContext.Provider value={{ user, authTokens, loginUser, logoutUser }}>
      {!loading ? children : <div>Loading...</div>}
    </AuthContext.Provider>
  );
};