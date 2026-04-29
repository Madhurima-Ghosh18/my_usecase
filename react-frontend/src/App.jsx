import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Header from './components/Header';
import TicketInput from './components/TicketInput';
import TicketInfo from './components/TicketInfo';
import SolutionCard from './components/SolutionCard';
import ChecklistCard from './components/ChecklistCard';
import NoRunbookFound from './components/NoRunbookFound';
import ErrorCard from './components/ErrorCard';
import LoadingSpinner from './components/LoadingSpinner';
import './App.css';

function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (ticketKey) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('/api/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ticket_key: ticketKey }),
      });

      const data = await response.json();

      if (data.success) {
        // Normal runbook matched
        setResult(data);
      } else if (data.no_runbook_match) {
        // No runbook found - show enhanced UI
        setResult(data);
      } else {
        // Other errors
        setError(data.error || 'Failed to process ticket');
      }
    } catch (err) {
      setError(`Network error: ${err.message}. Make sure Flask server is running on port 5000.`);
    } finally {
      setLoading(false);
    }
  };

  const handleRunbookCreated = (newRunbook) => {
    // Refresh or show success message
    setResult(null);
    setError(null);
    alert(`Runbook "${newRunbook.title}" created successfully! You can now process similar tickets.`);
  };

  return (
    <div className="app">
      <Header />
      
      <main className="main-container">
        <div className="content-wrapper">
          <TicketInput onSubmit={handleSubmit} loading={loading} />

          <AnimatePresence mode="wait">
            {loading && (
              <motion.div
                key="loading"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <LoadingSpinner />
              </motion.div>
            )}

            {error && !loading && (
              <motion.div
                key="error"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <ErrorCard error={error} onRetry={() => setError(null)} />
              </motion.div>
            )}

            {result && !loading && !error && (
              <motion.div
                key="results"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="results-container"
              >
                {result.no_runbook_match ? (
                  // No runbook found - show enhanced UI with options
                  <NoRunbookFound
                    ticket={result.ticket}
                    analysis={result.analysis}
                    genericChecklist={result.generic_checklist}
                    onRunbookCreated={handleRunbookCreated}
                  />
                ) : result.multiple_matches ? (
                  // Multiple runbooks matched
                  <>
                    <TicketInfo ticket={result.ticket} jiraUrl={result.jira_url} />
                    <div className="multiple-runbooks-alert">
                      <h3>🔧 Multiple Issues Detected</h3>
                      <p>{result.combined_solution}</p>
                      <div className="matched-runbooks-list">
                        {result.matched_runbooks.map((rb, idx) => (
                          <div key={idx} className="runbook-badge">
                            <strong>{rb.title}</strong>
                            <span className="score">Score: {rb.score}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    <ChecklistCard checklist={result.full_checklist} />
                  </>
                ) : (
                  // Single runbook matched
                  <>
                    <TicketInfo ticket={result.ticket} jiraUrl={result.jira_url} />
                    <SolutionCard
                      solution={result.one_line_solution}
                      runbook={result.runbook}
                    />
                    <ChecklistCard checklist={result.full_checklist} />
                  </>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>

      <footer className="footer">
        <p>Powered by AI • Llama-3.2-3B • HuggingFace • Built with React</p>
      </footer>
    </div>
  );
}

export default App;