import React, { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext({});

export const useAuth = () => {
  return useContext(AuthContext);
};

const DEFAULT_PASSWORD = "rratolip";
const AUTH_KEY = "pilotarr_auth";
const PASSWORD_KEY = "pilotarr_password";

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const stored = localStorage.getItem(AUTH_KEY);
    if (stored) {
      try {
        setUser(JSON.parse(stored));
      } catch {
        localStorage.removeItem(AUTH_KEY);
      }
    }
  }, []);

  const login = (username, password) => {
    const storedPassword = localStorage.getItem(PASSWORD_KEY) || DEFAULT_PASSWORD;
    if (username === "pilotarr" && password === storedPassword) {
      const userData = { username: "pilotarr" };
      setUser(userData);
      localStorage.setItem(AUTH_KEY, JSON.stringify(userData));
      return { ok: true };
    }
    return { ok: false, error: "Invalid credentials" };
  };

  const logout = () => {
    localStorage.removeItem(AUTH_KEY);
    setUser(null);
  };

  const changePassword = (currentPassword, newPassword) => {
    const storedPassword = localStorage.getItem(PASSWORD_KEY) || DEFAULT_PASSWORD;
    if (currentPassword !== storedPassword) {
      return { ok: false, error: "Current password is incorrect" };
    }
    localStorage.setItem(PASSWORD_KEY, newPassword);
    return { ok: true };
  };

  const value = {
    user,
    login,
    logout,
    changePassword,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
