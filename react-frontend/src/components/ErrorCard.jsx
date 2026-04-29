import React from 'react';
import { motion } from 'framer-motion';
import { FaExclamationTriangle, FaRedo } from 'react-icons/fa';
import './ErrorCard.css';

const ErrorCard = ({ error, onRetry }) => {
  return (
    <motion.div
      className="error-card"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
    >
      <div className="error-icon">
        <FaExclamationTriangle />
      </div>
      <h3>Error Processing Ticket</h3>
      <p className="error-message">{error}</p>
      <motion.button
        className="retry-button"
        onClick={onRetry}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <FaRedo /> Try Again
      </motion.button>
    </motion.div>
  );
};

export default ErrorCard;