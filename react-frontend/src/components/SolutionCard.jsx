import React from 'react';
import { motion } from 'framer-motion';
import { FaCheckCircle, FaBook } from 'react-icons/fa';
import './SolutionCard.css';

const SolutionCard = ({ solution, runbook }) => {
  return (
    <motion.div
      className="solution-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
    >
      <div className="card-header">
        <div className="header-left">
          <FaCheckCircle className="header-icon" />
          <h3>Resolution Summary</h3>
        </div>
        <span className="success-badge">Resolved</span>
      </div>

      <div className="solution-content">
        <div className="solution-main">
          <p className="solution-text">{solution}</p>
        </div>

        <div className="solution-meta">
          <div className="meta-item">
            <FaBook className="meta-icon" />
            <div className="meta-content">
              <span className="meta-label">Runbook:</span>
              <span className="meta-value">{runbook.title}</span>
            </div>
          </div>
          <div className="meta-item">
            <span className="category-badge">{runbook.category}</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default SolutionCard;