import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FaExclamationCircle, FaRobot, FaPlus, FaLightbulb } from 'react-icons/fa';
import RunbookCreator from './RunbookCreator';
import './NoRunbookFound.css';

const NoRunbookFound = ({ ticket, analysis, genericChecklist, onRunbookCreated }) => {
  const [showCreator, setShowCreator] = useState(false);
  const [showGenericSteps, setShowGenericSteps] = useState(false);

  const formatChecklist = (jiraMarkup) => {
    if (!jiraMarkup) return '';
    let text = jiraMarkup;
    text = text.replace(/h2\./g, '=====');
    text = text.replace(/h3\./g, '-----');
    text = text.replace(/\*/g, '');
    text = text.replace(/\[\]/g, '☐');
    return text;
  };

  if (showCreator) {
    return <RunbookCreator 
      analysis={analysis} 
      ticket={ticket}
      onBack={() => setShowCreator(false)}
      onCreated={onRunbookCreated}
    />;
  }

  return (
    <motion.div
      className="no-runbook-container"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="no-runbook-card">
        <div className="warning-icon">
          <FaExclamationCircle />
        </div>

        <h2>No Matching Runbook Found</h2>
        <p className="subtitle">
          We couldn't find an existing runbook for this incident type
        </p>

        {/* AI Analysis Section */}
        <div className="analysis-section">
          <div className="analysis-header">
            <FaRobot className="analysis-icon" />
            <h3>AI Analysis</h3>
          </div>
          
          <div className="analysis-details">
            <div className="analysis-item">
              <span className="analysis-label">Incident Type:</span>
              <span className="analysis-value">{analysis.incident_type}</span>
            </div>
            <div className="analysis-item">
              <span className="analysis-label">Category:</span>
              <span className="category-badge">{analysis.category}</span>
            </div>
            <div className="analysis-item">
              <span className="analysis-label">Confidence:</span>
              <span className={`confidence-badge confidence-${analysis.confidence.toLowerCase()}`}>
                {analysis.confidence}
              </span>
            </div>
          </div>
        </div>

        {/* Action Options */}
        <div className="action-section">
          <h3>What would you like to do?</h3>
          
          <div className="action-buttons">
            <motion.button
              className="action-btn primary-action"
              onClick={() => setShowCreator(true)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <FaPlus className="btn-icon" />
              <div className="btn-content">
                <span className="btn-title">Create New Runbook</span>
                <span className="btn-desc">Help the system learn</span>
              </div>
            </motion.button>

            <motion.button
              className="action-btn secondary-action"
              onClick={() => setShowGenericSteps(!showGenericSteps)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <FaLightbulb className="btn-icon" />
              <div className="btn-content">
                <span className="btn-title">Get Generic Steps</span>
                <span className="btn-desc">AI-generated guidance</span>
              </div>
            </motion.button>
          </div>
        </div>

        {/* Generic Steps Display */}
        {showGenericSteps && genericChecklist && (
          <motion.div
            className="generic-steps-section"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <div className="generic-steps-header">
              <h4>🤖 AI-Generated Troubleshooting Steps</h4>
              <span className="generic-badge">Temporary Guide</span>
            </div>
            <div className="generic-steps-content">
              <pre>{formatChecklist(genericChecklist)}</pre>
            </div>
            <div className="generic-steps-note">
              <strong>Note:</strong> These are generic steps. Please create a permanent 
              runbook after resolving the incident for better future handling.
            </div>
          </motion.div>
        )}

        {/* Ticket Info */}
        <div className="ticket-info-compact">
          <h4>Ticket Details</h4>
          <div className="ticket-detail-item">
            <strong>Key:</strong> {ticket.key}
          </div>
          <div className="ticket-detail-item">
            <strong>Summary:</strong> {ticket.summary}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default NoRunbookFound;