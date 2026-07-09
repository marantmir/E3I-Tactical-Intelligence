import { ScanLine, Video } from "lucide-react";

export default function VideoVisionPanel({ vision }) {
  return (
    <section className="vision-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Visao computacional</p>
          <h2>Mapa visual de movimentos</h2>
        </div>
        <span className="badge badge-high">Pronto para revisao</span>
      </div>
      <p>{vision.summary}</p>

      <div className="vision-layout">
        <div className="vision-field" aria-label="Mapa de calor e trilhas de movimentacao">
          {vision.heatmap.map((point, index) => (
            <span
              className="heat-point"
              key={`${point.x}-${point.y}-${index}`}
              style={{
                "--heat-size": `${28 + point.intensity / 3}px`,
                "--heat-opacity": `${0.32 + point.intensity / 220}`,
                left: `${point.x}%`,
                top: `${point.y}%`
              }}
            />
          ))}
          <svg viewBox="0 0 100 100" role="img">
            {vision.movement_tracks.map((track) => (
              <polyline
                className="movement-track"
                key={track.label}
                points={track.points.map((point) => `${point.x},${point.y}`).join(" ")}
              />
            ))}
            {vision.movement_tracks.flatMap((track) =>
              track.points.map((point, index) => (
                <circle
                  className="track-node"
                  cx={point.x}
                  cy={point.y}
                  key={`${track.label}-${index}`}
                  r={index === track.points.length - 1 ? 2.3 : 1.6}
                />
              ))
            )}
          </svg>
        </div>

        <div className="vision-events">
          {vision.frames.map((frame) => (
            <article key={frame.id}>
              <div>
                <Video size={16} />
                <strong>{frame.time}</strong>
                <span>{frame.confidence}</span>
              </div>
              <h3>{frame.focus}</h3>
              <p>{frame.title}</p>
            </article>
          ))}
        </div>
      </div>

      <div className="event-grid">
        {vision.events.map((event) => (
          <article key={`${event.minute}-${event.event}`}>
            <ScanLine size={17} />
            <h3>{event.minute}' - {event.event}</h3>
            <p>{event.finding}</p>
            <strong>{event.recommendation}</strong>
          </article>
        ))}
      </div>
    </section>
  );
}
