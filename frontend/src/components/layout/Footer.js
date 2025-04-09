import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="bg-gray-800 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="col-span-1 md:col-span-2">
            <Link to="/" className="text-xl font-bold text-white">
              StockAnalyzer
            </Link>
            <p className="mt-2 text-sm text-gray-300">
              A comprehensive platform for stock market analysis, trading simulation, 
              and portfolio management for Nifty 50 stocks.
            </p>
            <p className="mt-4 text-sm text-gray-400">
              Disclaimer: This application is for educational and simulation purposes only. 
              It does not constitute financial advice. Always consult with a professional 
              financial advisor before making investment decisions.
            </p>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
              Quick Links
            </h3>
            <ul className="mt-4 space-y-2">
              <li>
                <Link to="/" className="text-sm text-gray-300 hover:text-white">
                  Home
                </Link>
              </li>
              <li>
                <Link to="/stock-analysis" className="text-sm text-gray-300 hover:text-white">
                  Stock Analysis
                </Link>
              </li>
              <li>
                <Link to="/trading" className="text-sm text-gray-300 hover:text-white">
                  Trading Simulation
                </Link>
              </li>
              <li>
                <Link to="/dashboard" className="text-sm text-gray-300 hover:text-white">
                  Dashboard
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
              Resources
            </h3>
            <ul className="mt-4 space-y-2">
              <li>
                <a 
                  href="https://www.nseindia.com/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-sm text-gray-300 hover:text-white"
                >
                  NSE India
                </a>
              </li>
              <li>
                <a 
                  href="https://www.sebi.gov.in/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-sm text-gray-300 hover:text-white"
                >
                  SEBI
                </a>
              </li>
              <li>
                <a 
                  href="https://finance.yahoo.com/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-sm text-gray-300 hover:text-white"
                >
                  Yahoo Finance
                </a>
              </li>
              <li>
                <a 
                  href="https://www.moneycontrol.com/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-sm text-gray-300 hover:text-white"
                >
                  Money Control
                </a>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="mt-8 border-t border-gray-700 pt-8 flex flex-col md:flex-row justify-between">
          <p className="text-sm text-gray-400">
            &copy; {currentYear} StockAnalyzer. All rights reserved.
          </p>
          <p className="text-sm text-gray-400 mt-2 md:mt-0">
            Data provided by Yahoo Finance
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;