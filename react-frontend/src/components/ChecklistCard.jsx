import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaListUl, FaCopy, FaCheck, FaRedo, FaClipboard } from 'react-icons/fa';
import './ChecklistCard.css';

const ChecklistCard = ({ checklist, ticketKey }) => {
  const [copied, setCopied] = useState(false);
  const [commandCopied, setCommandCopied] = useState(null);
  const [completedSteps, setCompletedSteps] = useState({});
  const [parsedChecklist, setParsedChecklist] = useState([]);

  // Load saved state from localStorage
  useEffect(() => {
    if (ticketKey) {
      const saved = localStorage.getItem(`checklist-${ticketKey}`);
      if (saved) {
        setCompletedSteps(JSON.parse(saved));
      }
    }
  }, [ticketKey]);

  // Save state to localStorage whenever it changes
  useEffect(() => {
    if (ticketKey && Object.keys(completedSteps).length > 0) {
      localStorage.setItem(`checklist-${ticketKey}`, JSON.stringify(completedSteps));
    }
  }, [completedSteps, ticketKey]);

  // Parse checklist into structured format
  useEffect(() => {
    const parsed = parseChecklist(checklist);
    setParsedChecklist(parsed);
  }, [checklist]);

  const parseChecklist = (jiraMarkup) => {
    const lines = jiraMarkup.split('\n');
    const items = [];
    let currentSection = null;
    let stepNumber = 0;

    lines.forEach((line, idx) => {
      const trimmed = line.trim();

      // Section headers
      if (trimmed.startsWith('h3.') || trimmed.startsWith('-----')) {
        const sectionTitle = trimmed.replace(/^h3\.|^-+/, '').trim();
        if (sectionTitle) {
          currentSection = sectionTitle;
          items.push({
            type: 'section',
            title: sectionTitle,
            id: `section-${idx}`
          });
        }
      }
      // Checkboxes
      else if (trimmed.startsWith('[]')) {
        stepNumber++;
        const text = trimmed.replace('[]', '').trim();
        items.push({
          type: 'checkbox',
          text: text,
          id: `step-${stepNumber}`,
          section: currentSection
        });
      }
      // Numbered steps with bold markers
      else if (trimmed.match(/^\*?\d+\./)) {
        stepNumber++;
        const text = trimmed.replace(/^\*?(\d+)\.\s*/, '').replace(/\*$/, '').trim();
        
        // Look ahead for Command, Expected, Action
        const details = extractStepDetails(lines, idx);
        
        items.push({
          type: 'step',
          number: stepNumber,
          text: text,
          id: `step-${stepNumber}`,
          section: currentSection,
          command: details.command,
          expected: details.expected,
          action: details.action,
          warning: details.warning,
          lookFor: details.lookFor,
          check: details.check
        });
      }
      // Regular text (non-interactive)
      else if (trimmed && !trimmed.startsWith('*') && !trimmed.startsWith('-') && !trimmed.startsWith('h2.')) {
        items.push({
          type: 'text',
          text: trimmed,
          id: `text-${idx}`
        });
      }
    });

    return items;
  };

  const extractStepDetails = (lines, startIdx) => {
    const details = {
      command: null,
      expected: null,
      action: null,
      warning: null,
      lookFor: null,
      check: null
    };

    // Look at next 6 lines
    for (let i = startIdx + 1; i < Math.min(startIdx + 7, lines.length); i++) {
      const line = lines[i].trim();
      
      // Stop at next numbered step
      if (line.match(/^\*?\d+\./)) break;
      
      if (line.startsWith('Command:')) {
        details.command = line.replace('Command:', '').trim();
      } else if (line.startsWith('Expected:')) {
        details.expected = line.replace('Expected:', '').trim();
      } else if (line.startsWith('Action:')) {
        details.action = line.replace('Action:', '').trim();
      } else if (line.startsWith('Warning:')) {
        details.warning = line.replace('Warning:', '').trim();
      } else if (line.startsWith('Look for:')) {
        details.lookFor = line.replace('Look for:', '').trim();
      } else if (line.startsWith('Check:')) {
        details.check = line.replace('Check:', '').trim();
      }
    }

    return details;
  };

  const toggleStep = (stepId) => {
    setCompletedSteps(prev => ({
      ...prev,
      [stepId]: !prev[stepId]
    }));
  };

  const handleCopyAll = async () => {
    try {
      await navigator.clipboard.writeText(checklist);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleCopyCommand = async (command, stepId) => {
    try {
      await navigator.clipboard.writeText(command);
      setCommandCopied(stepId);
      setTimeout(() => setCommandCopied(null), 2000);
    } catch (err) {
      console.error('Failed to copy command:', err);
    }
  };

  const handleReset = () => {
    if (window.confirm('Reset all checkboxes? This will clear your progress.')) {
      setCompletedSteps({});
      if (ticketKey) {
        localStorage.removeItem(`checklist-${ticketKey}`);
      }
    }
  };

  const calculateProgress = () => {
    const checkableItems = parsedChecklist.filter(item => 
      item.type === 'checkbox' || item.type === 'step'
    );
    const completed = checkableItems.filter(item => completedSteps[item.id]).length;
    return checkableItems.length > 0 ? Math.round((completed / checkableItems.length) * 100) : 0;
  };

  const progress = calculateProgress();

  return (
    <motion.div
      className="checklist-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
    >
      <div className="card-header">
        <div className="header-left">
          <FaListUl className="header-icon" />
          <h3>Interactive Resolution Checklist</h3>
        </div>
        <div className="header-actions">
          <div className="progress-badge">
            {progress}% Complete
          </div>
          <motion.button
            className="reset-button"
            onClick={handleReset}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            title="Reset all checkboxes"
          >
            <FaRedo />
          </motion.button>
          <motion.button
            className={`copy-button ${copied ? 'copied' : ''}`}
            onClick={handleCopyAll}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {copied ? (
              <>
                <FaCheck /> Copied!
              </>
            ) : (
              <>
                <FaCopy /> Copy All
              </>
            )}
          </motion.button>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="progress-bar-container">
        <motion.div 
          className="progress-bar"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>

      <div className="checklist-content">
        {parsedChecklist.map((item, idx) => (
          <div key={item.id || idx}>
            {/* Section Header */}
            {item.type === 'section' && (
              <div className="section-header">
                <h4>{item.title}</h4>
              </div>
            )}

            {/* Simple Checkbox */}
            {item.type === 'checkbox' && (
              <motion.div 
                className={`checkbox-item ${completedSteps[item.id] ? 'completed' : ''}`}
                whileHover={{ x: 5 }}
              >
                <label>
                  <input
                    type="checkbox"
                    checked={completedSteps[item.id] || false}
                    onChange={() => toggleStep(item.id)}
                  />
                  <span className="checkbox-text">{item.text}</span>
                </label>
              </motion.div>
            )}

            {/* Numbered Step with Details */}
            {item.type === 'step' && (
              <motion.div 
                className={`step-item ${completedSteps[item.id] ? 'completed' : ''}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05 }}
              >
                <div className="step-header">
                  <label className="step-checkbox-label">
                    <input
                      type="checkbox"
                      checked={completedSteps[item.id] || false}
                      onChange={() => toggleStep(item.id)}
                    />
                    <span className="step-number">{item.number}.</span>
                    <span className="step-title">{item.text}</span>
                  </label>
                </div>

                {/* Step Details */}
                {(item.command || item.expected || item.action || item.warning || item.lookFor || item.check) && (
                  <div className="step-details">
                    {item.command && (
                      <div className="detail-row command-row">
                        <span className="detail-label">Command:</span>
                        <code className="detail-value">{item.command}</code>
                        <button
                          className={`copy-command-btn ${commandCopied === item.id ? 'copied' : ''}`}
                          onClick={() => handleCopyCommand(item.command, item.id)}
                          title="Copy command"
                        >
                          {commandCopied === item.id ? <FaCheck /> : <FaClipboard />}
                        </button>
                      </div>
                    )}

                    {item.expected && (
                      <div className="detail-row expected-row">
                        <span className="detail-label">Expected:</span>
                        <span className="detail-value">{item.expected}</span>
                      </div>
                    )}

                    {item.lookFor && (
                      <div className="detail-row lookfor-row">
                        <span className="detail-label">Look for:</span>
                        <span className="detail-value">{item.lookFor}</span>
                      </div>
                    )}

                    {item.check && (
                      <div className="detail-row check-row">
                        <span className="detail-label">Check:</span>
                        <span className="detail-value">{item.check}</span>
                      </div>
                    )}

                    {item.action && (
                      <div className="detail-row action-row">
                        <span className="detail-label">Action:</span>
                        <span className="detail-value">{item.action}</span>
                      </div>
                    )}

                    {item.warning && (
                      <div className="detail-row warning-row">
                        <span className="detail-label">⚠️ Warning:</span>
                        <span className="detail-value">{item.warning}</span>
                      </div>
                    )}
                  </div>
                )}
              </motion.div>
            )}
          </div>
        ))}
      </div>
    </motion.div>
  );
};

export default ChecklistCard;