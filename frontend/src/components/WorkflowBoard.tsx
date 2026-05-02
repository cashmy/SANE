import { workflowStages } from "../types/workflow";

const candidatePreview = [
  {
    source: "Weekly product newsletters",
    signal: "Likely low-value source",
    nextAction: "Review before recording a decision",
  },
  {
    source: "Retail promotion digests",
    signal: "High repetition, unclear future value",
    nextAction: "Human decision required",
  },
  {
    source: "Routine platform notices",
    signal: "Candidate for later rules and actions",
    nextAction: "Persist approved outcome",
  },
];

export function WorkflowBoard() {
  return (
    <section className="workflow-board" aria-labelledby="workflow-title">
      <header className="panel intro">
        <p className="eyebrow">Stage 1 scaffold</p>
        <h1 id="workflow-title">
          Inbound email governance, narrowed to the first loop.
        </h1>
        <p className="summary">
          SANE is scaffolded as a decision surface, not an email client. Gmail
          access, classification, and actions stay outside this slice until the
          human review path is proven.
        </p>
      </header>

      <section className="panel stages" aria-labelledby="stages-title">
        <h2 id="stages-title">
          Connect - Review Candidates - Decide - Complete
        </h2>
        <ol className="stage-grid">
          {workflowStages.map((stage, index) => (
            <li className="stage-card" key={stage.key}>
              <span className="stage-index">0{index + 1}</span>
              <div>
                <h3>{stage.label}</h3>
                <p>{stage.summary}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <section className="panel queue" aria-labelledby="queue-title">
        <h2 id="queue-title">Candidate queue placeholder</h2>
        <p className="queue-copy">
          This static queue is here to anchor the future UI surface for
          normalized candidates and explicit user decisions. No live Gmail data
          or AI suggestions are wired yet.
        </p>
        <ul className="candidate-list">
          {candidatePreview.map((candidate) => (
            <li className="candidate-item" key={candidate.source}>
              <strong>{candidate.source}</strong>
              <span>{candidate.signal}</span>
              <p>{candidate.nextAction}</p>
            </li>
          ))}
        </ul>
      </section>
    </section>
  );
}
