import React from 'react';
import { motion } from 'framer-motion';
import { FaClipboardList, FaExternalLinkAlt } from 'react-icons/fa';
import './TicketInfo.css';

const TicketInfo = ({ ticket, jiraUrl }) => {
  return (
    <motion.div
      className="ticket-info-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
    >
      <div className="card-header">
        <div className="header-left">
          <FaClipboardList className="header-icon" />
          <h3>Ticket Information</h3>
        </div>
        <a
          href={jiraUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="jira-link"
        >
          Open in Jira
          <FaExternalLinkAlt className="link-icon" />
        </a>
      </div>

      <div className="ticket-details">
        <div className="detail-item">
          <span className="detail-label">Ticket:</span>
          <span className="detail-value ticket-key">{ticket.key}</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Summary:</span>
          <span className="detail-value">{ticket.summary}</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Description:</span>
          <span className="detail-value">{ticket.description}</span>
        </div>
      </div>
    </motion.div>
  );
};

export default TicketInfo;