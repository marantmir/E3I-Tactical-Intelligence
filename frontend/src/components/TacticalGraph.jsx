import { Network } from "lucide-react";

export default function TacticalGraph({ graph }) {
  const nodesById = new Map(graph.nodes.map((node) => [node.id, node]));

  return (
    <section className="graph-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Grafos taticos</p>
          <h2>Conexoes e zonas de influencia</h2>
        </div>
        <span className="badge badge-high">{graph.formation.formation}</span>
      </div>

      <div className="graph-layout">
        <div className="graph-canvas" aria-label="Grafo tatico de conexoes">
          <svg viewBox="0 0 100 100" role="img">
            <defs>
              <marker id="graph-arrow" markerHeight="5" markerWidth="5" orient="auto" refX="4" refY="2.5">
                <path d="M0,0 L5,2.5 L0,5 Z" />
              </marker>
            </defs>
            {graph.edges.map((edge) => {
              const source = nodesById.get(edge.source);
              const target = nodesById.get(edge.target);
              if (!source || !target) return null;
              return (
                <line
                  className="graph-edge"
                  key={`${edge.source}-${edge.target}-${edge.label}`}
                  markerEnd="url(#graph-arrow)"
                  strokeWidth={Math.max(0.45, edge.weight / 16)}
                  x1={source.x}
                  x2={target.x}
                  y1={source.y}
                  y2={target.y}
                />
              );
            })}
            {graph.nodes.map((node) => (
              <g className={`graph-node graph-node-${node.type}`} key={node.id}>
                <circle cx={node.x} cy={node.y} r={node.type === "team" ? 6.4 : 4.8} />
                <text x={node.x} y={node.y - 7}>
                  {shortLabel(node.label)}
                </text>
              </g>
            ))}
          </svg>
        </div>

        <div className="graph-side">
          <article>
            <Network size={18} />
            <h3>Metricas de rede</h3>
            <dl className="meta-grid">
              <div>
                <dt>Centralidade</dt>
                <dd>{graph.metrics.centrality_leader}</dd>
              </div>
              <div>
                <dt>Densidade</dt>
                <dd>{graph.metrics.network_density}%</dd>
              </div>
              <div>
                <dt>Progressao</dt>
                <dd>{graph.metrics.progression_lane}</dd>
              </div>
              <div>
                <dt>Risco</dt>
                <dd>{graph.metrics.risk_lane}</dd>
              </div>
            </dl>
          </article>
          <article>
            <h3>Leituras acionaveis</h3>
            <ul className="check-list">
              {graph.insights.map((insight) => (
                <li key={insight}>{insight}</li>
              ))}
            </ul>
          </article>
        </div>
      </div>
    </section>
  );
}

function shortLabel(label) {
  const parts = label.split(" ");
  if (parts.length <= 2) return label;
  return `${parts[0]} ${parts.at(-1)}`;
}
