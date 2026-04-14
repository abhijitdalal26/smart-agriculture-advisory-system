import { generateAdvisory } from '../utils/advisoryGenerator';
import { AlertCircle, AlertTriangle, Lightbulb, MessageSquare } from 'lucide-react';

export default function AdvisoryPane({ sensors, predictions }) {
  const messages = generateAdvisory(sensors, predictions);

  const getIcon = (sev) => {
    if (sev === 'critical') return <AlertCircle size={20} />;
    if (sev === 'warning') return <AlertTriangle size={20} />;
    return <Lightbulb size={20} />;
  };

  return (
    <div className="card advisory-card advisory-row">
      <div className="card-title">
        <MessageSquare size={16} /> 
        AI Advisory — Natural Language Insights
      </div>
      <div className="advisory-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`advisory-msg ${msg.severity}`}>
            <span className="msg-icon">{getIcon(msg.severity)}</span>
            <span className="msg-text">{msg.text}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
