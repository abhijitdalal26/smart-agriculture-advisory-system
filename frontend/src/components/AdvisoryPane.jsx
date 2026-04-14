// AdvisoryPane — NLG advisory messages
import { generateAdvisory } from '../utils/advisoryGenerator';

export default function AdvisoryPane({ sensors, predictions }) {
  const messages = generateAdvisory(sensors, predictions);

  return (
    <div className="card advisory-card advisory-row">
      <div className="card-title">💬 AI Advisory — Natural Language Insights</div>
      <div className="advisory-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`advisory-msg ${msg.severity}`}>
            <span className="msg-icon">{msg.icon}</span>
            <span className="msg-text">{msg.text}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
