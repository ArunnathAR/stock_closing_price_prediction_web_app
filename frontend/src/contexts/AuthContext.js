import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [isAuthenticated, setIsAuthenticated] = useState(!!token);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if token exists and validate it
    const validateToken = async () => {
      if (token) {
        try {
          // Could add a verify endpoint to check token validity
          setIsAuthenticated(true);
          
          // Get user data from token
          const userDataString = localStorage.getItem('userData');
          if (userDataString) {
            setCurrentUser(JSON.parse(userDataString));
          }
        } catch (error) {
          console.error('Token validation error:', error);
          logout();
        }
      }
      setLoading(false);
    };

    validateToken();
  }, [token]);

  // Register new user
  const register = async (username, email, password) => {
    try {
      const response = await axios.post('/api/auth/register', {
        username,
        email,
        password
      });
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Registration error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed. Please try again.' 
      };
    }
  };

  // Login user
  const login = async (username, password) => {
    try {
      const response = await axios.post('/api/auth/login', {
        username,
        password
      });
      
      const { token, user_id, username: userName } = response.data;
      
      // Save token and user data
      localStorage.setItem('token', token);
      localStorage.setItem('userData', JSON.stringify({ 
        id: user_id, 
        username: userName 
      }));
      
      // Update context
      setToken(token);
      setCurrentUser({ id: user_id, username: userName });
      setIsAuthenticated(true);
      
      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed. Please check your credentials.' 
      };
    }
  };

  // Logout user
  const logout = async () => {
    try {
      if (token) {
        // Call logout API
        await axios.post('/api/auth/logout', {}, {
          params: { token }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local storage and state
      localStorage.removeItem('token');
      localStorage.removeItem('userData');
      setToken(null);
      setCurrentUser(null);
      setIsAuthenticated(false);
    }
  };

  // Set authentication headers for axios
  useEffect(() => {
    const setAuthHeader = () => {
      if (token) {
        axios.defaults.params = { 
          ...axios.defaults.params,
          token
        };
      } else {
        delete axios.defaults.params?.token;
      }
    };

    setAuthHeader();
  }, [token]);

  const value = {
    currentUser,
    isAuthenticated,
    loading,
    register,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};