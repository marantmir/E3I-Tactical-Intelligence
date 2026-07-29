import { Network } from "lucide-react";

export default function TacticalGraph({ graph }) {
  const nodesById = new Map(graph.nodes.map((node) => [node.id, node]));
  const influenceById = getInfluenceByNode(graph.nodes, graph.edges);

  return (
    <section className="graph-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Grafos táticos</p>
          <h2>Conexões e zonas de influência</h2>
        </div>
        <span className="badge badge-high">{graph.formation.formation}</span>
      </div>

      <div className="graph-layout">
        <div className="graph-canvas" aria-label="Grafo tático de conexões e zonas de influência">
          <svg viewBox="0 0 100 100" role="img">
            <title>Mapa das conexões e áreas de influência da equipe</title>
            <defs>
              <marker id="graph-arrow" markerHeight="4" markerWidth="4" orient="auto" refX="3.5" refY="2">
                <path d="M0,0 L5,2.5 L0,5 Z" />
              </marker>
              <radialGradient id="influence-team">
                <stop offset="0" stopColor="#f4c85d" stopOpacity=".34" />
                <stop offset=".62" stopColor="#d8a23a" stopOpacity=".13" />
                <stop offset="1" stopColor="#d8a23a" stopOpacity="0" />
              </radialGradient>
              <radialGradient id="influence-player">
                <stop offset="0" stopColor="#72c8ff" stopOpacity=".3" />
                <stop offset="1" stopColor="#4aa9e9" stopOpacity="0" />
              </radialGradient>
            </defs>
            <g className="graph-field-lines" aria-hidden="true">
              <line x1="50" x2="50" y1="8" y2="92" />
              <circle cx="50" cy="50" r="10" />
              <circle className="graph-field-spot" cx="50" cy="50" r="0.7" />
              <path d="M8 31 H20 V69 H8 M92 31 H80 V69 H92" />
              <path d="M8 40 H13 V60 H8 M92 40 H87 V60 H92" />
            </g>
            <g className="graph-influence-layer">
              {graph.nodes.map((node) => (
                <circle
                  className={`graph-influence graph-influence-${node.type}`}
                  cx={node.x}
                  cy={node.y}
                  key={`influence-${node.id}`}
                  r={influenceById.get(node.id).radius}
                />
              ))}
            </g>
            <g className="graph-edge-layer">
            {graph.edges.map((edge) => {
              const source = nodesById.get(edge.source);
              const target = nodesById.get(edge.target);
              if (!source || !target) return null;
              return (
                <line
                  className="graph-edge"
                  key={`${edge.source}-${edge.target}-${edge.label}`}
                  markerEnd="url(#graph-arrow)"
                  opacity={0.48 + Math.min(Number(edge.weight) || 0, 10) * 0.045}
                  strokeWidth={Math.min(2.8, Math.max(0.65, (Number(edge.weight) || 1) / 12))}
                  x1={source.x}
                  x2={target.x}
                  y1={source.y}
                  y2={target.y}
                />
              );
            })}
            </g>
            {graph.nodes.map((node) => (
              <g className={`graph-node graph-node-${node.type}`} key={node.id}>
                <circle className="graph-node-ring" cx={node.x} cy={node.y} r={node.type === "team" ? 6.4 : 4.8} />
                <circle className="graph-node-core" cx={node.x} cy={node.y} r={node.type === "team" ? 2.1 : 1.55} />
                <text x={node.x} y={node.y - (node.type === "team" ? 8.2 : 6.5)}>
                  {shortLabel(node.label)}
                </text>
              </g>
            ))}
          </svg>
          <div className="graph-legend" aria-label="Legenda do grafo">
            <span><i className="legend-zone" />Zona de influência</span>
            <span><i className="legend-link" />Conexão</span>
            <span><i className="legend-node" />Ator central</span>
          </div>
        </div>

        <div className="graph-side">
          <article>
            <Network size={18} />
            <h3>Métricas de rede</h3>
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
                <dt>Progressão</dt>
                <dd>{graph.metrics.progression_lane}</dd>
              </div>
              <div>
                <dt>Risco</dt>
                <dd>{graph.metrics.risk_lane}</dd>
              </div>
            </dl>
          </article>
          <article>
            <h3>Leituras acionáveis</h3>
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

function getInfluenceByNode(nodes, edges) {
  const totals = new Map(nodes.map((node) => [node.id, 0]));
  edges.forEach((edge) => {
    const weight = Number(edge.weight) || 1;
    totals.set(edge.source, (totals.get(edge.source) || 0) + weight);
    totals.set(edge.target, (totals.get(edge.target) || 0) + weight);
  });
  const peak = Math.max(...totals.values(), 1);
  return new Map(nodes.map((node) => {
    const normalized = (totals.get(node.id) || 0) / peak;
    return [node.id, { radius: 9 + normalized * 10 }];
  }));
}

function shortLabel(label) {
  const parts = label.split(" ");
  if (parts.length <= 2) return label;
  return `${parts[0]} ${parts.at(-1)}`;
}
