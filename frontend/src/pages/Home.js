import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Home = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="flex flex-col space-y-12">
      {/* Hero Section */}
      <section className="text-center py-12">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          AI-Powered Stock Market Analysis
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
          Make smarter trading decisions with our advanced stock price prediction, 
          technical analysis, and tax-aware trading simulations.
        </p>
        {isAuthenticated ? (
          <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4 justify-center">
            <Link to="/analysis" className="btn btn-primary px-8 py-3 text-base">
              Analyze Stocks
            </Link>
            <Link to="/dashboard" className="btn btn-secondary px-8 py-3 text-base">
              View Dashboard
            </Link>
          </div>
        ) : (
          <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4 justify-center">
            <Link to="/register" className="btn btn-primary px-8 py-3 text-base">
              Get Started
            </Link>
            <Link to="/login" className="btn btn-neutral px-8 py-3 text-base">
              Log In
            </Link>
          </div>
        )}
      </section>

      {/* Features Section */}
      <section className="py-12">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Smart Tools for Intelligent Investing
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Our platform combines multiple prediction models with technical analysis 
            to help you make data-driven investment decisions.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="card text-center">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-100 text-blue-600 mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Advanced Stock Analysis</h3>
            <p className="text-gray-600">
              Analyze Nifty 50 stocks with our ensemble prediction model that combines LSTM, ARIMA, and Prophet algorithms.
            </p>
          </div>

          <div className="card text-center">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-green-100 text-green-600 mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Tax-Aware Trading</h3>
            <p className="text-gray-600">
              Calculate taxes and potential profits for your trades based on Indian tax laws for short-term and long-term investments.
            </p>
          </div>

          <div className="card text-center">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-purple-100 text-purple-600 mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Personalized Dashboard</h3>
            <p className="text-gray-600">
              Track your portfolio, watchlist, and analysis history in one place with real-time data updates.
            </p>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-12 bg-gray-50 rounded-lg">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            How StockSage Works
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Our platform simplifies the stock analysis process with just a few steps.
          </p>
        </div>

        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-start">
            <div className="md:w-1/4 mb-8 md:mb-0 text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-600 text-white font-bold text-xl mb-4">
                1
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Select Stock</h3>
              <p className="text-gray-600">
                Choose from the Nifty 50 stocks and select your analysis period (1, 3, or 5 months).
              </p>
            </div>

            <div className="md:w-1/4 mb-8 md:mb-0 text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-600 text-white font-bold text-xl mb-4">
                2
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Get Predictions</h3>
              <p className="text-gray-600">
                Our AI models analyze historical data and generate price predictions with detailed visualizations.
              </p>
            </div>

            <div className="md:w-1/4 mb-8 md:mb-0 text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-600 text-white font-bold text-xl mb-4">
                3
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Trade Simulation</h3>
              <p className="text-gray-600">
                Simulate buy/sell transactions with built-in tax calculations to understand potential returns.
              </p>
            </div>

            <div className="md:w-1/4 text-center">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-600 text-white font-bold text-xl mb-4">
                4
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Track Performance</h3>
              <p className="text-gray-600">
                Monitor your portfolio, track your analysis history, and compare predictions with actual performance.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-12 text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Ready to Make Smarter Investment Decisions?
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto mb-8">
          Join thousands of investors using our platform to analyze stocks and optimize their trading strategies.
        </p>
        {isAuthenticated ? (
          <Link to="/analysis" className="btn btn-primary px-8 py-3 text-base">
            Start Analyzing Now
          </Link>
        ) : (
          <Link to="/register" className="btn btn-primary px-8 py-3 text-base">
            Create Your Free Account
          </Link>
        )}
      </section>
    </div>
  );
};

export default Home;