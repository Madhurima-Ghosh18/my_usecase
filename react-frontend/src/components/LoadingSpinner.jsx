import React from 'react';
import { motion } from 'framer-motion';
import { FaRobot } from 'react-icons/fa';
import './LoadingSpinner.css';

const LoadingSpinner = () => {
  return (
    <motion.div
      className="loading-spinner-card"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
    >
      <div className="spinner-container">
        <motion.div
          className="spinner-icon"
          animate={{
            rotate: 360,
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'linear',
          }}
        >
          <FaRobot />
        </motion.div>
        <h3>Processing Your Ticket</h3>
        <p>AI is analyzing the incident and selecting the best runbook...</p>
        
        <div className="progress-steps">
          <motion.div
            className="step"
            initial={{ opacity: 0.3 }}
            animate={{ opacity: 1 }}
            transition={{ repeat: Infinity, duration: 1.5, delay: 0 }}
          >
            <span className="step-dot"></span>
            <span>Fetching ticket data</span>
          </motion.div>
          <motion.div
            className="step"
            initial={{ opacity: 0.3 }}
            animate={{ opacity: 1 }}
            transition={{ repeat: Infinity, duration: 1.5, delay: 0.5 }}
          >
            <span className="step-dot"></span>
            <span>AI runbook selection</span>
          </motion.div>
          <motion.div
            className="step"
            initial={{ opacity: 0.3 }}
            animate={{ opacity: 1 }}
            transition={{ repeat: Infinity, duration: 1.5, delay: 1 }}
          >
            <span className="step-dot"></span>
            <span>Generating checklist</span>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
};

export default LoadingSpinner;