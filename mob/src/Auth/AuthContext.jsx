import React, { createContext, useState, useEffect } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import jwtDecode from "jwt-decode";
import { useNavigation } from "@react-navigation/native";

const AuthContext = createContext();
export default AuthContext;

const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL; // For Expo env

export const AuthProvider = ({ children }) => {
  const navigation = useNavigation();

  const [authTokens, setAuthTokens] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // --- Load tokens from AsyncStorage on startup ---
  useEffect(() => {
    const loadTokens = async () => {
      try {
        const storedTokens = await AsyncStorage.getItem("authTokens");

        if (storedTokens) {
          const parsed = JSON.parse(storedTokens);
          setAuthTokens(parsed);
          setUser(jwtDecode(parsed.access));
        }
      } catch (err) {
        console.error("Error loading tokens:", err);
      }

      setLoading(false);
    };

    loadTokens();
  }, []);

  // --- Safe jwt decode ---
  const safeDecode = (token) => {
    try {
      return jwtDecode(token);
    } catch (err) {
      console.error("Invalid token:", err);
      return null;
    }
  };

  // --- LOGIN USER ---
  const loginUser = async (username, password) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/token/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        alert("Invalid username or password");
        return;
      }

      const data = await response.json();

      await AsyncStorage.setItem("authTokens", JSON.stringify(data));
      setAuthTokens(data);
      setUser(safeDecode(data.access));

      navigation.navigate("Chat"); // React-Native routing
    } catch (err) {
      console.error("Login error:", err);
      alert("Login failed");
    }
  };

  // --- LOGOUT USER ---
  const logoutUser = async () => {
    setAuthTokens(null);
    setUser(null);
    await AsyncStorage.removeItem("authTokens");
    navigation.navigate("Login");
  };

  // --- Refresh token ---
  const updateToken = async () => {
    if (!authTokens?.refresh) {
      logoutUser();
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/token/refresh/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh: authTokens.refresh }),
      });

      if (!response.ok) {
        logoutUser();
        return;
      }

      const data = await response.json();

      const decoded = safeDecode(data.access);
      if (!decoded) {
        logoutUser();
        return;
      }

      await AsyncStorage.setItem("authTokens", JSON.stringify(data));

      setAuthTokens(data);
      setUser(decoded);

    } catch (err) {
      console.error("Refresh error:", err);
      logoutUser();
    }
  };

  // --- Auto-refresh every 4 minutes ---
  useEffect(() => {
    if (!loading) {
      const interval = setInterval(() => {
        if (authTokens) updateToken();
      }, 1000 * 60 * 4);
      return () => clearInterval(interval);
    }
  }, [authTokens, loading]);

  return (
    <AuthContext.Provider
      value={{
        user,
        authTokens,
        loginUser,
        logoutUser,
      }}
    >
      {!loading ? children : null}
    </AuthContext.Provider>
  );
};
