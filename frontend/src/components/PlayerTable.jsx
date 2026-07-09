import ConfidenceBadge from "./ConfidenceBadge.jsx";

export default function PlayerTable({ players }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Jogador</th>
            <th>Posição</th>
            <th>Idade</th>
            <th>Min</th>
            <th>G</th>
            <th>A</th>
            <th>Nota</th>
            <th>Influência</th>
            <th>Risco</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {players.map((player) => (
            <tr key={`${player.team_id}-${player.name}`}>
              <td>
                <strong>{player.name}</strong>
                <span>{player.highlight}</span>
              </td>
              <td>{player.position}</td>
              <td>{player.age}</td>
              <td>{player.minutes}</td>
              <td>{player.goals}</td>
              <td>{player.assists}</td>
              <td>{player.tactical_score}</td>
              <td>{player.influence}</td>
              <td>
                <ConfidenceBadge level={player.risk_level} />
              </td>
              <td>{player.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
