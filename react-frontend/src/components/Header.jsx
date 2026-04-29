import React from 'react';
import { motion } from 'framer-motion';
import { FaRobot } from 'react-icons/fa';
import './Header.css';

const Header = () => {
  return (
    <motion.header
      className="header"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ type: 'spring', stiffness: 100 }}
    >
      <div className="header-content">
        <div className="logo">
          <FaRobot className="logo-icon" />
          <h1>AI Incident Management</h1>
        </div>
        
        <div className="status-badge">
          <span className="status-dot"></span>
          <span>System Ready</span>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;