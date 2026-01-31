import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { signalsAPI, billingAPI } from '../services/api';
import '../styles/Dashboard.css';

function Dashboard() {
  const { user, loading, logout, refreshUser } = useAuth();
  const navigate = useNavigate();
  const [signals, setSignals] = useState([]);
  const [userLimit, setUserLimit] = useState('');
  const [loadingSignals, setLoadingSignals] = useState(true);
  const [error, setError] = useState('');
  const [checkoutLoading, setCheckoutLoading] = useState(false);

  // Redirect to login if not authenticated (only after auth is initialized)
  useEffect(() => {
    if (!loading && !user) {
      navigate('/login');
    }
  }, [user, loading, navigate]);

  // Fetch signals when user is loaded
  useEffect(() => {
    if (user) {
      fetchSignals();
    }
  }, [user]);

  const fetchSignals = async () => {
    setLoadingSignals(true);
    setError('');
    try {
      const response = await signalsAPI.getSignals();
      setSignals(response.data.signals);
      setUserLimit(response.data.user_limit || '');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch signals');
    } finally {
      setLoadingSignals(false);
    }
  };

  const handleSubscribe = async () => {
    setCheckoutLoading(true);
    try {
      const successUrl = `${window.location.origin}/dashboard?success=true`;
      const cancelUrl = `${window.location.origin}/dashboard?canceled=true`;
      const response = await billingAPI.createCheckout(successUrl, cancelUrl);
      
      // Redirect to Stripe Checkout
      window.location.href = response.data.checkout_url;
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create checkout session');
      setCheckoutLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Check for payment success/cancel in URL
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('success') === 'true') {
      alert('Payment successful! Your subscription is now active.');
      refreshUser();
      // Clean URL
      window.history.replaceState({}, '', '/dashboard');
    } else if (params.get('canceled') === 'true') {
      alert('Payment canceled.');
      // Clean URL
      window.history.replaceState({}, '', '/dashboard');
    }
  }, [refreshUser]);

  if (loading) {
    return <div className="loading">Authenticating...</div>;
  }

  if (loadingSignals) {
    return <div className="loading">Loading signals...</div>;
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Trading Signals Dashboard</h1>
        <div className="header-actions">
          <span className="user-email">{user?.email}</span>
          <button onClick={handleLogout} className="btn-secondary">Logout</button>
        </div>
      </header>

      <div className="subscription-status">
        <h2>Subscription Status</h2>
        <div className={`status-badge ${user?.is_paid ? 'paid' : 'free'}`}>
          {user?.is_paid ? '✓ Paid Plan' : 'Free Plan'}
        </div>
        {!user?.is_paid && (
          <div className="upgrade-section">
            <p>Upgrade to unlock unlimited signals!</p>
            <button 
              onClick={handleSubscribe} 
              disabled={checkoutLoading}
              className="btn-primary btn-subscribe"
            >
              {checkoutLoading ? 'Redirecting...' : 'Subscribe for ₹499'}
            </button>
          </div>
        )}
        {userLimit && <p className="limit-info">{userLimit}</p>}
      </div>

      <div className="signals-section">
        <div className="section-header">
          <h2>Trading Signals</h2>
          <button onClick={fetchSignals} className="btn-refresh">Refresh</button>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="signals-table">
          <table>
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Type</th>
                <th>Price</th>
                <th>Confidence</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {signals.map((signal, index) => (
                <tr key={index}>
                  <td className="symbol">{signal.symbol}</td>
                  <td>
                    <span className={`signal-type ${signal.type.toLowerCase()}`}>
                      {signal.type}
                    </span>
                  </td>
                  <td>₹{signal.price.toFixed(2)}</td>
                  <td>{(signal.confidence * 100).toFixed(0)}%</td>
                  <td>{new Date(signal.timestamp).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
