import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FaArrowLeft, FaSave, FaRobot, FaSpinner } from 'react-icons/fa';
import './RunbookCreator.css';

const RunbookCreator = ({ analysis, ticket, onBack, onCreated }) => {
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('');
  const [keywords, setKeywords] = useState('');
  const [steps, setSteps] = useState('');
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    // Pre-fill with AI suggestions
    if (analysis) {
      setTitle(analysis.incident_type || '');
      setCategory(analysis.category || '');
      setKeywords(analysis.keywords || '');
    }
  }, [analysis]);

  const generateDraft = async () => {
    setGenerating(true);
    try {
      const response = await fetch('/api/generate-runbook-draft', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ analysis, ticket }),
      });

      const data = await response.json();
      
      if (data.success) {
        setTitle(data.draft.title);
        setCategory(data.draft.category);
        setKeywords(data.draft.keywords);
        setSteps(data.draft.steps);
      }
    } catch (error) {
      console.error('Draft generation failed:', error);
    } finally {
      setGenerating(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('/api/create-runbook', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, category, keywords, steps }),
      });

      const data = await response.json();

      if (data.success) {
        setSaveSuccess(true);
        setTimeout(() => {
          onCreated && onCreated(data.runbook);
        }, 2000);
      }
    } catch (error) {
      console.error('Failed to create runbook:', error);
      alert('Failed to create runbook. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (saveSuccess) {
    return (
      <motion.div
        className="success-message"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
      >
        <div className="success-icon">✅</div>
        <h2>Runbook Created Successfully!</h2>
        <p>The system will now use this runbook for similar incidents.</p>
      </motion.div>
    );
  }

  return (
    <motion.div
      className="runbook-creator"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="creator-header">
        <button className="back-btn" onClick={onBack}>
          <FaArrowLeft /> Back
        </button>
        <h2>Create New Runbook</h2>
        <button
          className="generate-btn"
          onClick={generateDraft}
          disabled={generating}
        >
          {generating ? (
            <>
              <FaSpinner className="spinner" /> Generating...
            </>
          ) : (
            <>
              <FaRobot /> AI Generate Draft
            </>
          )}
        </button>
      </div>

      <form onSubmit={handleSubmit} className="creator-form">
        <div className="form-section">
          <label htmlFor="title">
            Runbook Title <span className="required">*</span>
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., Email Service Failure Resolution"
            required
          />
          <small>Clear, descriptive title for this runbook</small>
        </div>

        <div className="form-row">
          <div className="form-section">
            <label htmlFor="category">
              Category <span className="required">*</span>
            </label>
            <input
              type="text"
              id="category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="e.g., email, api, network"
              required
            />
            <small>Single word category</small>
          </div>

          <div className="form-section">
            <label htmlFor="keywords">
              Keywords <span className="required">*</span>
            </label>
            <input
              type="text"
              id="keywords"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              placeholder="e.g., email,smtp,sendgrid,notification"
              required
            />
            <small>Comma-separated keywords</small>
          </div>
        </div>

        <div className="form-section">
          <label htmlFor="steps">
            Resolution Steps <span className="required">*</span>
          </label>
          <textarea
            id="steps"
            value={steps}
            onChange={(e) => setSteps(e.target.value)}
            placeholder={`Enter numbered resolution steps:

1. Check service status
Command: systemctl status email-service
Expected: Service should be 'active (running)'

2. Verify configuration
File: /etc/email/config.yaml
Check: SMTP credentials are correct

... (continue with detailed steps)`}
            rows={20}
            required
          />
          <small>
            Detailed, numbered steps with commands and expected results
          </small>
        </div>

        <div className="form-actions">
          <button type="button" className="btn-cancel" onClick={onBack}>
            Cancel
          </button>
          <button
            type="submit"
            className="btn-submit"
            disabled={loading || !title || !category || !keywords || !steps}
          >
            {loading ? (
              <>
                <FaSpinner className="spinner" /> Saving...
              </>
            ) : (
              <>
                <FaSave /> Create Runbook
              </>
            )}
          </button>
        </div>
      </form>
    </motion.div>
  );
};

export default RunbookCreator;