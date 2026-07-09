export default function MetricCard({ icon: Icon, label, value, tone = "neutral" }) {
  return (
    <article className={`metric metric-${tone}`}>
      <div className="metric-icon" aria-hidden="true">
        {Icon ? <Icon size={20} /> : null}
      </div>
      <div>
        <p>{label}</p>
        <strong>{value}</strong>
      </div>
    </article>
  );
}
