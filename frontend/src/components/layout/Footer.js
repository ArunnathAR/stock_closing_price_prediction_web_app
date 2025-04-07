import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="bg-white shadow-inner mt-auto">
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <span className="text-xl font-bold text-blue-600">StockSage</span>
            <p className="text-sm text-gray-600 mt-1">
              Your AI-powered stock market analysis platform
            </p>
          </div>
          <div className="flex flex-col md:flex-row md:space-x-8">
            <div className="mt-4 md:mt-0">
              <h3 className="text-sm font-semibold text-gray-800 mb-2">Navigation</h3>
              <ul className="space-y-2">
                <li>
                  <Link to="/" className="text-sm text-gray-600 hover:text-blue-600">
                    Home
                  </Link>
                </li>
                <li>
                  <Link to="/analysis" className="text-sm text-gray-600 hover:text-blue-600">
                    Stock Analysis
                  </Link>
                </li>
                <li>
                  <Link to="/trading" className="text-sm text-gray-600 hover:text-blue-600">
                    Trading
                  </Link>
                </li>
                <li>
                  <Link to="/dashboard" className="text-sm text-gray-600 hover:text-blue-600">
                    Dashboard
                  </Link>
                </li>
              </ul>
            </div>
            <div className="mt-4 md:mt-0">
              <h3 className="text-sm font-semibold text-gray-800 mb-2">Legal</h3>
              <ul className="space-y-2">
                <li>
                  <a href="#" className="text-sm text-gray-600 hover:text-blue-600">
                    Terms of Service
                  </a>
                </li>
                <li>
                  <a href="#" className="text-sm text-gray-600 hover:text-blue-600">
                    Privacy Policy
                  </a>
                </li>
                <li>
                  <a href="#" className="text-sm text-gray-600 hover:text-blue-600">
                    Disclaimer
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
        <div className="mt-8 border-t border-gray-200 pt-4">
          <p className="text-sm text-gray-600 text-center">
            &copy; {new Date().getFullYear()} StockSage. All rights reserved.
          </p>
          <p className="text-xs text-gray-500 text-center mt-2">
            This application is for educational purposes only. Not financial advice.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;