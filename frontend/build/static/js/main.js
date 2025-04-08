console.log('StockAnalyzer frontend is loading...');
document.addEventListener('DOMContentLoaded', function() {
  const rootElement = document.getElementById('root');
  if (rootElement) {
    rootElement.innerHTML = `
      <div style="max-width: 800px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
        <h1 style="color: #2962FF; text-align: center;">StockAnalyzer</h1>
        <div style="background-color: #f0f4f8; border-radius: 8px; padding: 20px; margin-top: 20px;">
          <h2 style="color: #333;">Welcome to StockAnalyzer</h2>
          <p>The full React interface is currently being built. The backend API is fully functional.</p>
          <h3 style="margin-top: 20px;">Available API Endpoints:</h3>
          <ul style="margin-top: 10px;">
            <li><code>/api/stocks/list</code> - Get list of available Nifty 50 stocks</li>
            <li><code>/api/stocks/data?symbol=SYMBOL&period=PERIOD</code> - Get stock price data</li>
            <li><code>/api/stocks/price?symbol=SYMBOL</code> - Get current stock price</li>
            <li><code>/api/prediction?symbol=SYMBOL&period=PERIOD</code> - Get price prediction</li>
          </ul>
          <div style="margin-top: 30px; text-align: center;">
            <a href="/api/stocks/list" style="display: inline-block; padding: 10px 20px; background-color: #2962FF; color: white; text-decoration: none; border-radius: 4px; margin-right: 10px;">
              View Stocks API
            </a>
            <a href="/docs" style="display: inline-block; padding: 10px 20px; background-color: #00C853; color: white; text-decoration: none; border-radius: 4px;">
              API Documentation
            </a>
          </div>
        </div>
      </div>
    `;
  }
});
