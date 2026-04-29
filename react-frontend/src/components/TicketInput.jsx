import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FaTicketAlt, FaArrowRight } from 'react-icons/fa';
import './TicketInput.css';

const TicketInput = ({ onSubmit, loading }) => {
  const [ticketKey, setTicketKey] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (ticketKey.trim()) {
      onSubmit(ticketKey.trim());
    }
  };

  return (
    <motion.div
      className="ticket-input-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
    >
      <div className="card-header">
        <FaTicketAlt className="header-icon" />
        <h2>Enter Ticket Information</h2>
      </div>

      <form onSubmit={handleSubmit} className="ticket-form">
        <div className="form-group">
          <label htmlFor="ticketKey">Ticket Key</label>
          <input
            type="text"
            id="ticketKey"
            value={ticketKey}
            onChange={(e) => setTicketKey(e.target.value)}
            placeholder="e.g., AIM-1, IM-45, INC-123"
            disabled={loading}
            className="ticket-input"
            autoFocus
          />
          <p className="input-hint">Enter the Jira ticket key you want to process</p>
        </div>

        <motion.button
          type="submit"
          className="submit-button"
          disabled={loading || !ticketKey.trim()}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          {loading ? (
            <>
              <span className="spinner"></span>
              Processing...
            </>
          ) : (
            <>
              Analyze Ticket
              <FaArrowRight className="button-icon" />
            </>
          )}
        </motion.button>
      </form>
    </motion.div>
  );
};

export default TicketInput;