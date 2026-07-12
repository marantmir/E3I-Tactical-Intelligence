import { useState } from "react";
import {
  Activity,
  Circle,
  Flame,
  GitBranch,
  ListFilter,
  Route,
  ScanLine,
  SlidersHorizontal,
  Target,
  UploadCloud,
  Video
} from "lucide-react";

import { api } from "../api/client.js";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "";
const TEAM_FILTERS = [
  { key: "reference", label: "Camisas enviadas" },
  { key: "auto", label: "Automatico" },
  { key: "all", label: "Todas as equipes" },
  { key: "light", label: "Uniforme claro em campo" },
  { key: "dark", label: "Uniforme escuro em campo" },
  { key: "red", label: "Vermelho" },
  { key: "blue", label: "Azul" },
  { key: "green", label: "Verde" },
  { key: "yellow", label: "Amarelo" },
  { key: "orange", label: "Laranja" },
  { key: "purple", label: "Roxo" }
];

export default function VideoVisionPanel({ teamRef, teamName }) {
  const [vision, setVision] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState(null);
  const [videoError, setVideoError] = useState(null);
  const [fileName, setFileName] = useState("");
  const [viewMode, setViewMode] = useState("connections");
  const [selectedTrackId, setSelectedTrackId] = useState("all");
  const [maxFrames, setMaxFrames] = useState(240);
  const [sampleEvery, setSampleEvery] = useState(3);
  const [teamFilter, setTeamFilter] = useState("auto");
  const [jerseyFiles, setJerseyFiles] = useState([]);
  const [savingFormation, setSavingFormation] = useState(false);
  const [formationSaveMessage, setFormationSaveMessage] = useState("");
  const [layers, setLayers] = useState({
    heatmap: true,
    tracks: true,
    connections: true,
    ball: true
  });

  const videoUrl = vision?.annotated_video_url ? `${API_BASE}${vision.annotated_video_url}` : "";
  const movementTracks = vision?.movement_tracks || [];
  const selectedTracks =
    selectedTrackId === "all"
      ? movementTracks
      : movementTracks.filter((track) => String(track.id) === String(selectedTrackId));
  const trackLookup = new Map(movementTracks.map((track) => [Number(track.id), track]));
  const visibleTrackIds = new Set(selectedTracks.map((track) => Number(track.id)));
  const connectionLimit = viewMode === "connections" ? 34 : 18;
  const connectionEdges = (vision?.graph?.edges || [])
    .filter((edge) => visibleTrackIds.has(Number(edge.source)) && visibleTrackIds.has(Number(edge.target)))
    .sort((a, b) => b.weight - a.weight)
    .slice(0, connectionLimit);
  const selectedTrack = selectedTrackId === "all" ? null : selectedTracks[0];
  const strongestConnection = connectionEdges[0];
  const heatmapPoints = viewMode === "events" ? vision?.ball_heatmap || [] : vision?.heatmap || [];
  const ballTrack = vision?.ball_track || [];
  const isLocalTeam = /^\d+$/.test(String(teamRef));
  const shapeAnalysis = vision?.shape_analysis;
  const canSaveFormation = isLocalTeam && shapeAnalysis?.formation_guess && shapeAnalysis.formation_guess !== "Indefinida";

  async function handleFileChange(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    setLoading(true);
    setProgress(null);
    setError(null);
    setVideoError(null);
    setSelectedTrackId("all");
    setVision(null);
    setFormationSaveMessage("");
    try {
      const result = await api.uploadVideoVisionWithProgress(
        teamRef,
        file,
        { maxFrames, sampleEvery, teamName, teamFilter, jerseyFiles },
        (update) => setProgress(update)
      );
      setVision(result);
    } catch (uploadError) {
      setError(uploadError.message || "Falha ao processar o video.");
    } finally {
      setLoading(false);
      setProgress(null);
    }
  }

  async function handleSaveDetectedFormation() {
    if (!shapeAnalysis) return;
    setSavingFormation(true);
    setFormationSaveMessage("");
    try {
      const confidence = shapeAnalysis.confidence || "Baixa";
      const probability = confidence === "Media" ? 55 : confidence === "Alta" ? 70 : 30;
      await api.saveDetectedFormation(teamRef, {
        formation: shapeAnalysis.formation_guess,
        probability,
        context: `Detectado por visao computacional em ${vision.frames_analyzed || 0} frames analisados (${
          shapeAnalysis.block || "bloco nao identificado"
        }).`,
        advantages: shapeAnalysis.explanation || "",
        risks: "Estimativa automatica por posicao media dos rastros; valide com mais videos e leitura manual."
      });
      setFormationSaveMessage(`Formacao "${shapeAnalysis.formation_guess}" salva no time.`);
    } catch (saveError) {
      setFormationSaveMessage(saveError.message || "Falha ao salvar a formacao detectada.");
    } finally {
      setSavingFormation(false);
    }
  }

  return (
    <section className="vision-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Visao computacional</p>
          <h2>Analise tatica visual do video</h2>
        </div>
        {vision && <span className="badge badge-high">{vision.tracks_detected} rastros validos</span>}
      </div>

      <div className="vision-processing-controls">
        <SlidersHorizontal size={17} />
        <label>
          <span>Frames analisados</span>
          <input
            max="1200"
            min="60"
            onChange={(event) => setMaxFrames(Number(event.target.value))}
            step="60"
            type="range"
            value={maxFrames}
          />
          <strong>{maxFrames}</strong>
        </label>
        <label>
          <span>Intervalo entre frames</span>
          <input
            max="12"
            min="1"
            onChange={(event) => setSampleEvery(Number(event.target.value))}
            step="1"
            type="range"
            value={sampleEvery}
          />
          <strong>{sampleEvery}</strong>
        </label>
        <label className="team-filter-select">
          <span>Equipe a rastrear</span>
          <select value={teamFilter} onChange={(event) => setTeamFilter(event.target.value)}>
            {TEAM_FILTERS.map((option) => (
              <option key={option.key} value={option.key}>
                {option.label}
              </option>
            ))}
          </select>
          <strong>{teamFilter === "auto" ? "auto" : "manual"}</strong>
        </label>
      </div>

      <label className="jersey-reference-upload">
        <Target size={18} />
        <span>
          {jerseyFiles.length
            ? `${jerseyFiles.length} camisa(s) de referencia anexada(s)`
            : "Anexar camisa(s) do time para melhorar a identificacao"}
        </span>
        <input
          type="file"
          accept="image/*"
          multiple
          onChange={(event) => {
            const files = Array.from(event.target.files || []);
            setJerseyFiles(files);
            if (files.length) setTeamFilter("reference");
          }}
          hidden
        />
      </label>
      {jerseyFiles.length > 0 ? (
        <div className="jersey-reference-list">
          {jerseyFiles.map((file) => (
            <span key={`${file.name}-${file.size}`}>{file.name}</span>
          ))}
        </div>
      ) : null}

      <label className="video-upload-dropzone">
        <UploadCloud size={20} />
        <span>{fileName || "Enviar video do jogo (.mp4, .mov, .avi, .mkv, .webm)"}</span>
        <input type="file" accept="video/*" onChange={handleFileChange} hidden />
      </label>

      {loading ? <VideoProcessingProgress progress={progress} /> : null}
      {error && <p className="error-text">{error}</p>}

      {vision && (
        <>
          <p>{vision.summary}</p>
          {vision.team_focus ? (
            <div className="notice-strip">
              Acompanhando {teamName}: {vision.team_focus.selected_label}. {vision.team_focus.target_tracks} rastros
              usados nos padroes.
            </div>
          ) : null}
          {vision.field_candidate_filter ? (
            <p className="video-caption">{vision.field_candidate_filter.strategy}</p>
          ) : null}
          {vision.jersey_reference?.enabled ? (
            <div className="notice-strip">
              {vision.jersey_reference.count} camisa(s) usada(s) como referencia visual para identificar {teamName}.
            </div>
          ) : null}
          {vision.upload_profile?.safe_mode_applied ? (
            <div className="notice-strip">
              Perfil seguro aplicado ao video ({vision.upload_profile.size_mb}MB):{" "}
              {vision.upload_profile.effective_max_frames} frames, intervalo{" "}
              {vision.upload_profile.effective_sample_every}. Isso evita timeout em arquivos grandes/MKV.
            </div>
          ) : null}
          {vision.processing_config?.full_video_coverage ? (
            <div className="notice-strip">
              Amostragem distribuida do inicio ao fim do video enviado ({vision.processing_config.source_total_frames}{" "}
              frames de origem, 1 amostra a cada {vision.processing_config.sample_every} frames) para representar a
              partida completa, nao apenas os primeiros segundos.
            </div>
          ) : null}
          {vision.processing_config?.stopped_by_timeout ? (
            <div className="notice-strip">
              Analise parcial gerada antes do limite de {vision.processing_config.max_processing_seconds}s. Para leitura
              mais profunda, envie um recorte menor do lance.
            </div>
          ) : null}

          <div className="vision-controls">
            <div className="segmented-control" aria-label="Modo de leitura visual">
              <button
                className={viewMode === "overview" ? "active" : ""}
                type="button"
                onClick={() => setViewMode("overview")}
              >
                <Activity size={15} />
                Geral
              </button>
              <button
                className={viewMode === "connections" ? "active" : ""}
                type="button"
                onClick={() => setViewMode("connections")}
              >
                <GitBranch size={15} />
                Conexoes
              </button>
              <button
                className={viewMode === "tracks" ? "active" : ""}
                type="button"
                onClick={() => setViewMode("tracks")}
              >
                <Route size={15} />
                Trilhas
              </button>
              <button
                className={viewMode === "events" ? "active" : ""}
                type="button"
                onClick={() => setViewMode("events")}
              >
                <ListFilter size={15} />
                Eventos
              </button>
            </div>

            <div className="layer-toggles">
              <label>
                <input
                  checked={layers.heatmap}
                  onChange={() => setLayers((current) => ({ ...current, heatmap: !current.heatmap }))}
                  type="checkbox"
                />
                Heatmap
              </label>
              <label>
                <input
                  checked={layers.tracks}
                  onChange={() => setLayers((current) => ({ ...current, tracks: !current.tracks }))}
                  type="checkbox"
                />
                Trilhas
              </label>
              <label>
                <input
                  checked={layers.connections}
                  onChange={() => setLayers((current) => ({ ...current, connections: !current.connections }))}
                  type="checkbox"
                />
                Conexoes
              </label>
              <label>
                <input
                  checked={layers.ball}
                  onChange={() => setLayers((current) => ({ ...current, ball: !current.ball }))}
                  type="checkbox"
                />
                Bola
              </label>
            </div>

            <label className="track-select">
              Trilha
              <select value={selectedTrackId} onChange={(event) => setSelectedTrackId(event.target.value)}>
                <option value="all">Todas as principais</option>
                {movementTracks.map((track) => (
                  <option key={track.id} value={track.id}>
                    {track.label} - {track.team_label || "equipe"} - {track.role_hint || "funcao a revisar"}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="vision-layout">
            <div>
              <video
                key={vision.annotated_video_url}
                controls
                autoPlay
                muted
                loop
                playsInline
                preload="metadata"
                onError={() =>
                  setVideoError("O navegador nao conseguiu reproduzir o video anotado automaticamente.")
                }
                style={{ width: "100%", borderRadius: "8px", background: "#000" }}
              >
                <source src={videoUrl} type={vision.annotated_video_mime || "video/webm"} />
              </video>
              {videoError && (
                <p className="error-text">
                  {videoError}{" "}
                  <a href={videoUrl} target="_blank" rel="noreferrer">
                    Abrir video anotado
                  </a>
                </p>
              )}
              <p className="video-caption">
                Overlay: caixas, IDs persistentes, trilhas, bola provavel, tercos, corredores e leitura
                tatica. {vision.frames_analyzed} frames analisados; replay em{" "}
                {vision.output_fps || vision.source_fps} fps ({vision.annotated_video_codec || "codec automatico"}).
              </p>
            </div>

            <div className="vision-field" aria-label="Mapa 2D de campo com trilhas, bola e conexoes">
              {layers.heatmap &&
                heatmapPoints.map((point, index) => (
                  <span
                    className={viewMode === "events" ? "heat-point heat-point-ball" : "heat-point"}
                    key={`${point.x}-${point.y}-${index}`}
                    style={{
                      "--heat-size": `${10 + point.intensity / 5}px`,
                      "--heat-opacity": `${0.12 + point.intensity / 460}`,
                      left: `${point.x}%`,
                      top: `${point.y}%`
                    }}
                  />
                ))}

              <svg viewBox="0 0 100 100" role="img">
                <FieldLines />
                {layers.connections &&
                  connectionEdges.map((edge) => {
                    const source = lastPoint(trackLookup.get(Number(edge.source)));
                    const target = lastPoint(trackLookup.get(Number(edge.target)));
                    if (!source || !target) return null;
                    return (
                      <line
                        className="proximity-edge"
                        key={`${edge.source}-${edge.target}`}
                        style={{ "--edge-weight": Math.min(3.8, 0.9 + edge.weight / 24) }}
                        x1={source.x}
                        x2={target.x}
                        y1={source.y}
                        y2={target.y}
                      />
                    );
                  })}
                {layers.tracks &&
                  selectedTracks.map((track) => {
                    const points = fieldPoints(track);
                    return (
                      <polyline
                        className="movement-track"
                        key={track.id}
                        points={points.map((point) => `${point.x},${point.y}`).join(" ")}
                      />
                    );
                  })}
                {layers.ball && ballTrack.length > 1 && (
                  <polyline
                    className="ball-track"
                    points={ballTrack.map((point) => `${point.x},${point.y}`).join(" ")}
                  />
                )}
                {layers.tracks &&
                  selectedTracks.flatMap((track) =>
                    fieldPoints(track).map((point, index, points) => (
                      <circle
                        className="track-node"
                        cx={point.x}
                        cy={point.y}
                        key={`${track.id}-${index}`}
                        r={index === points.length - 1 ? 2.2 : 1.3}
                      />
                    ))
                  )}
                {layers.ball &&
                  ballTrack.map((point, index) => (
                    <circle
                      className="ball-node"
                      cx={point.x}
                      cy={point.y}
                      key={`${point.frame}-${index}`}
                      r={index === ballTrack.length - 1 ? 1.9 : 1.1}
                    />
                  ))}
              </svg>
            </div>
          </div>

          <div className="vision-analysis-grid">
            <article>
              <Flame size={17} />
              <h3>Padrao dominante</h3>
              <p>{vision.tactical_summary}</p>
              <strong>{vision.movement_tracks_shown} trilhas organizadas para revisao</strong>
            </article>
            <article>
              <GitBranch size={17} />
              <h3>Rede selecionada</h3>
              <p>{connectionSummary(strongestConnection, trackLookup)}</p>
              <strong>{connectionEdges.length} conexoes visiveis no filtro atual</strong>
            </article>
            <article>
              <Route size={17} />
              <h3>Funcao em campo</h3>
              <p>{trackSummary(selectedTrack, movementTracks)}</p>
              <strong>{selectedTrack ? `${selectedTrack.total_samples} amostras` : "Todas as trilhas principais"}</strong>
            </article>
          </div>

          <div className="vision-analysis-grid">
            <article>
              <Target size={17} />
              <h3>Equipe acompanhada</h3>
              <p>{vision.team_focus?.note || "Filtro por equipe aplicado ao processamento visual."}</p>
              <strong>
                {vision.team_focus?.selected_label || "Automatico"} - {vision.team_focus?.target_tracks || 0} rastros
              </strong>
            </article>
            <article>
              <Target size={17} />
              <h3>Referencia de camisa</h3>
              <p>{vision.jersey_reference?.note || "Anexe uma ou mais imagens da camisa para refinar o filtro."}</p>
              <strong>
                {vision.jersey_reference?.enabled
                  ? `${vision.jersey_reference.count} referencia(s) ativas`
                  : "Sem camisa anexada"}
              </strong>
            </article>
            <article>
              <ScanLine size={17} />
              <h3>Filtro anti-torcida</h3>
              <p>Objetos fora do gramado, faixas largas e formas pouco compativeis com jogador sao descartados.</p>
              <strong>{rejectionSummary(vision.field_candidate_filter?.rejections)}</strong>
            </article>
            <article>
              <h3>Estrutura coletiva</h3>
              <p>{vision.shape_analysis?.explanation || "Estrutura ainda nao estimada para este trecho."}</p>
              <strong>
                {vision.shape_analysis?.formation_guess || "Indefinida"} - {vision.shape_analysis?.block || "sem bloco"}
              </strong>
              {canSaveFormation ? (
                <div className="formation-save-row">
                  <button
                    className="button button-secondary"
                    type="button"
                    onClick={handleSaveDetectedFormation}
                    disabled={savingFormation}
                  >
                    <Target size={15} />
                    {savingFormation ? "Salvando..." : "Salvar como formacao do time"}
                  </button>
                  {formationSaveMessage ? <span className="inline-message">{formationSaveMessage}</span> : null}
                </div>
              ) : null}
            </article>
            <article>
              <ScanLine size={17} />
              <h3>Campo e homografia</h3>
              <p>{vision.field_model?.explanation || "Campo lido por normalizacao direta do frame."}</p>
              <strong>{vision.field_model?.detection_rate || 0}% dos frames com campo detectado</strong>
            </article>
            <article>
              <Circle size={17} />
              <h3>Bola provavel</h3>
              <p>A trilha da bola e usada para sugerir passes, finalizacoes e zonas de circulacao.</p>
              <strong>{ballTrack.length} pontos exibidos no mapa 2D</strong>
            </article>
          </div>

          {vision.team_focus?.available_groups?.length > 0 ? (
            <div className="team-focus-groups">
              {vision.team_focus.available_groups.map((group) => (
                <article className={group.selected ? "selected" : ""} key={group.key}>
                  <strong>{group.label}</strong>
                  <span>{group.tracks} rastros / {group.samples} amostras</span>
                </article>
              ))}
            </div>
          ) : null}

          <section className="identity-technique-panel">
            <div>
              <p className="eyebrow">Identidade do jogador</p>
              <h3>Numero e nome na camisa</h3>
            </div>
            <div className="event-grid">
              {(vision.player_identity_strategy?.steps || []).map((step) => (
                <article key={step}>
                  <p>{step}</p>
                </article>
              ))}
            </div>
          </section>

          {vision.llm_identity ? (
            <section className="identity-technique-panel ai-insight-panel">
              <div>
                <p className="eyebrow">LLM + OCR visual</p>
                <h3>Hipoteses de time, jogador e numero</h3>
                <p>{vision.llm_identity.summary}</p>
              </div>
              {vision.llm_identity.candidates?.length > 0 ? (
                <div className="event-grid">
                  {vision.llm_identity.candidates.slice(0, 8).map((candidate) => (
                    <article key={`${candidate.track_id}-${candidate.number}-${candidate.player}`}>
                      <h3>Track {candidate.track_id ?? "N/A"}</h3>
                      <p>
                        {candidate.player || "nao identificado"} - camisa{" "}
                        {candidate.number || "nao identificado"}
                      </p>
                      <strong>
                        {candidate.role_hint || "funcao a revisar"} - {candidate.confidence || "Baixa"}
                      </strong>
                    </article>
                  ))}
                </div>
              ) : null}
              {vision.llm_identity.number_name_method?.length > 0 ? (
                <ul className="check-list">
                  {vision.llm_identity.number_name_method.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              ) : null}
            </section>
          ) : null}

          {vision.llm_analysis ? (
            <section className="ai-insight-panel">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">Analise gerada por LLM</p>
                  <h3>O que esta acontecendo visualmente</h3>
                </div>
                <span className="badge badge-medium">{vision.llm_analysis.provider || "IA"}</span>
              </div>
              <p>{vision.llm_analysis.executive_summary}</p>
              <div className="vision-analysis-grid">
                <article>
                  <h3>Padroes taticos</h3>
                  <ul className="check-list">
                    {(vision.llm_analysis.tactical_patterns || []).map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </article>
                <article>
                  <h3>Decisoes sugeridas</h3>
                  <ul className="check-list">
                    {(vision.llm_analysis.decision_points || []).map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </article>
                <article>
                  <h3>Riscos de leitura</h3>
                  <ul className="check-list">
                    {(vision.llm_analysis.risks || []).map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </article>
              </div>
            </section>
          ) : null}

          {vision.pattern_explanations?.length > 0 && (
            <div className="event-grid">
              {vision.pattern_explanations.map((item) => (
                <article key={item.title}>
                  <ScanLine size={16} />
                  <h3>{item.title}</h3>
                  <p>{item.why_it_matters}</p>
                  <strong>{item.evidence}</strong>
                </article>
              ))}
            </div>
          )}

          <div className="section-heading">
            <div>
              <p className="eyebrow">Eventos-alvo</p>
              <h3>Lista usada na inferencia visual</h3>
            </div>
          </div>
          <div className="event-target-list">
            {(vision.event_targets || []).map((target) => (
              <article key={target.key}>
                <strong>{target.label}</strong>
                <span>{target.description}</span>
              </article>
            ))}
          </div>

          <div className="section-heading">
            <div>
              <p className="eyebrow">Grafo de proximidade real</p>
              <h3>Conexoes entre rastros detectados</h3>
            </div>
          </div>
          <div className="event-grid">
            <article>
              <ScanLine size={17} />
              <h3>Densidade da rede: {vision.graph.metrics.network_density}%</h3>
              <p>Lider de centralidade: {vision.graph.metrics.centrality_leader || "N/A"}</p>
              <strong>{vision.graph.metrics.total_proximity_events} eventos de proximidade detectados</strong>
            </article>
            <article>
              <Video size={17} />
              <h3>Modo de processamento</h3>
              <p>{vision.visual_report?.processing_note || "Processamento local em batch com OpenCV."}</p>
              <strong>{vision.processing_config?.sample_every} frame(s) de intervalo por amostra</strong>
            </article>
          </div>

          {vision.tactical_events?.length > 0 && (
            <div className="event-grid">
              {vision.tactical_events.map((event) => (
                <article key={`${event.time_s}-${event.type}`}>
                  <ScanLine size={16} />
                  <h3>{event.time_s}s - {event.type}</h3>
                  <p>{event.finding}</p>
                  <strong>{event.active_tracks} rastros ativos no trecho</strong>
                </article>
              ))}
            </div>
          )}

          {vision.events?.length > 0 && (
            <div className="event-grid">
              {vision.events.map((event, index) => (
                <article key={`${event.frame}-${event.type}-${event.track_id}-${index}`}>
                  <Video size={16} />
                  <h3>
                    {event.time_s}s - {event.label || event.type}
                  </h3>
                  <p>{event.explanation || "Evento visual inferido pelo comportamento dos rastros."}</p>
                  <strong>
                    Track {event.track_id ?? "N/A"} - confianca {event.confidence || "Baixa"}
                  </strong>
                </article>
              ))}
            </div>
          )}
        </>
      )}
    </section>
  );
}

function FieldLines() {
  return (
    <g className="field-lines">
      <rect x="4" y="4" width="92" height="92" rx="1.4" />
      <line x1="50" x2="50" y1="4" y2="96" />
      <circle cx="50" cy="50" r="9" />
      <rect x="4" y="26" width="14" height="48" />
      <rect x="82" y="26" width="14" height="48" />
      <rect x="4" y="37" width="6" height="26" />
      <rect x="90" y="37" width="6" height="26" />
      <circle cx="50" cy="50" r="0.9" />
      <circle cx="13" cy="50" r="0.8" />
      <circle cx="87" cy="50" r="0.8" />
    </g>
  );
}

function fieldPoints(track) {
  return track?.pitch_points?.length ? track.pitch_points : track?.points || [];
}

function lastPoint(track) {
  const points = fieldPoints(track);
  if (!points.length) return null;
  return points[points.length - 1];
}

function connectionSummary(edge, trackLookup) {
  if (!edge) return "Selecione trilhas ou habilite conexoes para revisar relacoes de proximidade.";
  const source = trackLookup.get(Number(edge.source));
  const target = trackLookup.get(Number(edge.target));
  if (!source || !target) return "Conexao sem trilhas visiveis no filtro atual.";
  return `${source.label} conectado a ${target.label}; relacao espacial recorrente com peso ${edge.weight}.`;
}

function trackSummary(selectedTrack, tracks) {
  if (selectedTrack) {
    return `${selectedTrack.label} (${selectedTrack.team_label || "equipe filtrada"}) aparece como ${
      selectedTrack.role_hint || "funcao a revisar"
    } e percorreu ${Math.round(
      selectedTrack.distance_px || 0
    )}px no recorte analisado.`;
  }
  if (!tracks.length) return "Nenhuma trilha principal ficou disponivel para este video.";
  const leader = [...tracks].sort((a, b) => (b.distance_px || 0) - (a.distance_px || 0))[0];
  return `${leader.label} teve a maior movimentacao entre as trilhas principais; funcao provavel: ${
    leader.role_hint || "a revisar"
  }.`;
}

function rejectionSummary(rejections = {}) {
  const total = Object.values(rejections).reduce((sum, value) => sum + Number(value || 0), 0);
  if (!total) return "Nenhum candidato descartado nesta amostra";
  const main = Object.entries(rejections).sort((a, b) => Number(b[1]) - Number(a[1]))[0];
  return `${total} candidato(s) descartado(s); principal motivo: ${main[0].replaceAll("_", " ")}`;
}

function VideoProcessingProgress({ progress }) {
  const processed = progress?.processed || 0;
  const maxFrames = progress?.max_frames || 0;
  const percent = maxFrames > 0 ? Math.min(100, Math.round((processed / maxFrames) * 100)) : 0;

  return (
    <div className="video-progress" role="status" aria-live="polite">
      <div className="video-progress-track">
        <div className="video-progress-fill" style={{ width: `${percent}%` }} />
      </div>
      <p>
        {maxFrames > 0
          ? `Analisando ao vivo: ${processed} de ${maxFrames} amostras processadas (${percent}%).`
          : "Iniciando processamento com OpenCV, tracking e leitura tatica..."}
      </p>
    </div>
  );
}
