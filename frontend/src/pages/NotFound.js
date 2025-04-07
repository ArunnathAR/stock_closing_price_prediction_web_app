import React from 'react';
import { Link } from 'react-router-dom';

const NotFound = () => {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <div className="text-6xl font-bold text-blue-600 mb-4">404</div>
      <h1 className="text-2xl font-bold text-gray-800 mb-4">Page Not Found</h1>
      <p className="text-gray-600 text-center mb-8 max-w-md">
        The page you are looking for doesn't exist or has been moved.
      </p>
      <Link to="/" className="btn btn-primary">
        Go to Home
      </Link>
    </div>
  );
};

export default NotFound;