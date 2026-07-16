/**
 * Real-time Video Analysis Streaming Component
 *
 * Visualizes player movements in real-time from WebSocket stream:
 * - Soccer field rendering
 * - Live player positions by team
 * - Player trajectories/trails
 * - Proximity edges between nearby players
 * - Real-time statistics
 * - Support for file upload and URL input
 */
import React, { useState, useEffect, useRef } from 'react';
import './VideoAnalysisStreaming.css';

const VideoAnalysisStreaming = () => {
  const canvasRef = useRef(null);
  const uploadInputRef = useRef(null);
  const wsRef = useRef(null);

  const [videoId, setVideoId] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [metadata, setMetadata] = useState(null);
  const [stats, setStats] = useState({
    frameIdx: 0,
    totalPlayers: 0,
    fps: 0,
    timestamp: 0,
    proximities: 0,
  });
  const [error, setError] = useState(null);
  const [uploadMode, setUploadMode] = useState('file'); // 'file' or 'url'
  const [videoUrl, setVideoUrl] = useState('');
  const [teamNames, setTeamNames] = useState({ '0': 'Team A', '1': 'Team B' });

  // Canvas state for rendering
  const playerTracksRef = useRef(new Map()); // player_id -> [points]
  const teamColorsRef = useRef({ 0: '#E63946', 1: '#457B9D' }); // Red and Blue teams
  const lastFrameRef = useRef(null);

  const FIELD_WIDTH = 105; // FIFA standard in meters
  const FIELD_HEIGHT = 68;
  const TRAIL_LENGTH = 20; // Keep last N positions for trail

  /**
   * Draw soccer field with markings - realistic perspective
   */
  const drawField = (ctx, width, height) => {
    // Calculate field dimensions with padding
    const padding = 20;
    const availableWidth = width - padding * 2;
    const availableHeight = height - padding * 2;

    const scale = Math.min(availableWidth / FIELD_WIDTH, availableHeight / FIELD_HEIGHT);
    const fieldWidth = FIELD_WIDTH * scale;
    const fieldHeight = FIELD_HEIGHT * scale;

    const offsetX = (width - fieldWidth) / 2;
    const offsetY = (height - fieldHeight) / 2;

    // Gradient background for depth
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, '#0d3a1a');
    gradient.addColorStop(0.5, '#1a5a2e');
    gradient.addColorStop(1, '#0d3a1a');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);

    // Field background
    ctx.fillStyle = '#1a6d3a';
    ctx.fillRect(offsetX, offsetY, fieldWidth, fieldHeight);

    // Field lines
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2.5;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    // Outer border
    ctx.strokeRect(offsetX, offsetY, fieldWidth, fieldHeight);

    // Center line
    ctx.beginPath();
    ctx.moveTo(offsetX + fieldWidth / 2, offsetY);
    ctx.lineTo(offsetX + fieldWidth / 2, offsetY + fieldHeight);
    ctx.stroke();

    // Center circle
    ctx.beginPath();
    ctx.arc(
      offsetX + fieldWidth / 2,
      offsetY + fieldHeight / 2,
      9.15 * scale,
      0,
      2 * Math.PI
    );
    ctx.stroke();

    // Center spot
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(
      offsetX + fieldWidth / 2,
      offsetY + fieldHeight / 2,
      0.4 * scale,
      0,
      2 * Math.PI
    );
    ctx.fill();

    // Corner arcs
    const cornerRadius = 1 * scale;
    [
      [offsetX, offsetY],
      [offsetX + fieldWidth, offsetY],
      [offsetX + fieldWidth, offsetY + fieldHeight],
      [offsetX, offsetY + fieldHeight],
    ].forEach(([cx, cy]) => {
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.arc(cx, cy, cornerRadius, 0, 2 * Math.PI);
      ctx.stroke();
    });

    // Penalty areas (with arcs)
    const penaltyWidth = 16.5 * scale;
    const penaltyHeight = 40.32 * scale;
    const penaltyArcRadius = 9.15 * scale;

    // Left penalty area
    ctx.strokeRect(offsetX, offsetY + (fieldHeight - penaltyHeight) / 2, penaltyWidth, penaltyHeight);
    ctx.beginPath();
    ctx.arc(
      offsetX + penaltyWidth,
      offsetY + fieldHeight / 2,
      penaltyArcRadius,
      0,
      2 * Math.PI
    );
    ctx.stroke();

    // Right penalty area
    ctx.strokeRect(
      offsetX + fieldWidth - penaltyWidth,
      offsetY + (fieldHeight - penaltyHeight) / 2,
      penaltyWidth,
      penaltyHeight
    );
    ctx.beginPath();
    ctx.arc(
      offsetX + fieldWidth - penaltyWidth,
      offsetY + fieldHeight / 2,
      penaltyArcRadius,
      0,
      2 * Math.PI
    );
    ctx.stroke();

    // Goal areas
    const goalWidth = 5.5 * scale;
    const goalHeight = 18.32 * scale;

    // Left goal area
    ctx.strokeRect(offsetX, offsetY + (fieldHeight - goalHeight) / 2, goalWidth, goalHeight);

    // Right goal area
    ctx.strokeRect(
      offsetX + fieldWidth - goalWidth,
      offsetY + (fieldHeight - goalHeight) / 2,
      goalWidth,
      goalHeight
    );

    return { scale, offsetX, offsetY, fieldWidth, fieldHeight };
  };

  /**
   * Convert field coordinates to canvas coordinates
   */
  const fieldToCanvas = (x, y, fieldInfo) => {
    const canvasX = fieldInfo.offsetX + x * fieldInfo.scale;
    const canvasY = fieldInfo.offsetY + y * fieldInfo.scale;

    return {
      x: canvasX,
      y: canvasY,
      scale: fieldInfo.scale,
    };
  };

  /**
   * Render frame with players, trajectories, and edges
   */
  const renderFrame = (graphData, proximities) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Draw field
    const fieldInfo = drawField(ctx, width, height);

    // Update player tracks and validate they're in field bounds
    const teams = graphData.teams || {};
    Object.entries(teams).forEach(([teamId, players]) => {
      players?.forEach((player) => {
        // Only track players within field bounds
        if (player.x >= 0 && player.x <= FIELD_WIDTH &&
            player.y >= 0 && player.y <= FIELD_HEIGHT) {
          const trackKey = `${teamId}_${player.player_id}`;
          if (!playerTracksRef.current.has(trackKey)) {
            playerTracksRef.current.set(trackKey, []);
          }

          const track = playerTracksRef.current.get(trackKey);
          track.push({ x: player.x, y: player.y });

          // Keep only last N positions
          if (track.length > TRAIL_LENGTH) {
            track.shift();
          }
        }
      });
    });

    // Draw trajectories (trails) - subtle
    Object.entries(teams).forEach(([teamId, players]) => {
      const teamColor = teamColorsRef.current[parseInt(teamId)];
      players?.forEach((player) => {
        // Only draw trails for valid positions
        if (player.x >= 0 && player.x <= FIELD_WIDTH &&
            player.y >= 0 && player.y <= FIELD_HEIGHT) {
          const trackKey = `${teamId}_${player.player_id}`;
          const track = playerTracksRef.current.get(trackKey) || [];

          if (track.length > 1) {
            ctx.strokeStyle = `${teamColor}25`; // Very transparent
            ctx.lineWidth = 1.5;
            ctx.beginPath();

            track.forEach((point, idx) => {
              const canvas_pos = fieldToCanvas(point.x, point.y, fieldInfo);
              if (idx === 0) {
                ctx.moveTo(canvas_pos.x, canvas_pos.y);
              } else {
                ctx.lineTo(canvas_pos.x, canvas_pos.y);
              }
            });

            ctx.stroke();
          }
        }
      });
    });

    // Draw proximity edges
    ctx.strokeStyle = '#FFD60A40'; // Semi-transparent yellow
    ctx.lineWidth = 1.5;
    proximities?.forEach((prox) => {
      // Find player positions
      let pos1, pos2;
      Object.values(teams).forEach((players) => {
        const p1 = players?.find((p) => p.player_id === prox.source);
        const p2 = players?.find((p) => p.player_id === prox.target);
        if (p1) pos1 = p1;
        if (p2) pos2 = p2;
      });

      if (pos1 && pos2) {
        const c1 = fieldToCanvas(pos1.x, pos1.y, fieldInfo);
        const c2 = fieldToCanvas(pos2.x, pos2.y, fieldInfo);

        ctx.beginPath();
        ctx.moveTo(c1.x, c1.y);
        ctx.lineTo(c2.x, c2.y);
        ctx.stroke();
      }
    });

    // Draw players with number badges
    Object.entries(teams).forEach(([teamId, players]) => {
      const teamColor = teamColorsRef.current[parseInt(teamId)];

      players?.forEach((player) => {
        // Only render players within field bounds
        if (player.x >= 0 && player.x <= FIELD_WIDTH &&
            player.y >= 0 && player.y <= FIELD_HEIGHT) {
          const canvasPos = fieldToCanvas(player.x, player.y, fieldInfo);
          const playerNum = player.player_id % 11 || 11; // 1-11 instead of 0-10

          // Draw player marker (circle)
          ctx.fillStyle = teamColor;
          ctx.beginPath();
          ctx.arc(canvasPos.x, canvasPos.y, 8, 0, 2 * Math.PI);
          ctx.fill();

          // Player outline (white)
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.arc(canvasPos.x, canvasPos.y, 8, 0, 2 * Math.PI);
          ctx.stroke();

          // Number badge background (darker)
          const badgeRadius = 12;
          ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
          ctx.beginPath();
          ctx.arc(canvasPos.x + 8, canvasPos.y - 8, badgeRadius, 0, 2 * Math.PI);
          ctx.fill();

          // Number badge border
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 1.5;
          ctx.stroke();

          // Player number
          ctx.fillStyle = '#ffffff';
          ctx.font = 'bold 14px Arial';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(playerNum, canvasPos.x + 8, canvasPos.y - 8);
        }
      });
    });

    // Draw stats overlay
    drawStatsOverlay(ctx, graphData, proximities, width, height);
  };

  /**
   * Draw statistics overlay
   */
  const drawStatsOverlay = (ctx, graphData, proximities, width, height) => {
    const padding = 10;
    ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
    ctx.fillRect(padding, padding, 250, 150);

    ctx.fillStyle = '#ffffff';
    ctx.font = '12px Arial';
    ctx.textAlign = 'left';

    let y = padding + 15;
    const lineHeight = 18;

    ctx.fillText(`Frame: ${graphData.frame_idx || 0}`, padding + 10, y);
    y += lineHeight;

    ctx.fillText(`Time: ${(graphData.timestamp || 0).toFixed(2)}s`, padding + 10, y);
    y += lineHeight;

    ctx.fillText(
      `Players: ${graphData.total_players || 0}`,
      padding + 10,
      y
    );
    y += lineHeight;

    ctx.fillText(
      `Proximities: ${proximities?.length || 0}`,
      padding + 10,
      y
    );
    y += lineHeight;

    // Team info
    const teams = graphData.teams || {};
    Object.entries(teams).forEach(([teamId, players]) => {
      const teamColor = teamColorsRef.current[parseInt(teamId)];
      const teamName = teamNames[teamId] || (teamId === '0' ? 'Team A' : 'Team B');

      ctx.fillStyle = teamColor;
      ctx.fillRect(padding + 10, y - 10, 8, 8);

      ctx.fillStyle = '#ffffff';
      ctx.fillText(`${teamName}: ${players?.length || 0}`, padding + 25, y);
      y += lineHeight;
    });
  };

  /**
   * Handle video upload from file
   */
  const handleVideoUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('team_names', JSON.stringify(teamNames));

      const response = await fetch('/api/videos/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data = await response.json();
      initializeVideo(data);
    } catch (err) {
      setError(err.message);
      console.error('Upload error:', err);
    } finally {
      setIsUploading(false);
    }
  };

  /**
   * Handle video upload from URL
   */
  const handleUrlSubmit = async () => {
    if (!videoUrl.trim()) {
      setError('Please enter a valid video URL');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        video_url: videoUrl,
        team_names: JSON.stringify(teamNames),
      });

      const response = await fetch(`/api/videos/upload-url?${params}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data = await response.json();
      initializeVideo(data);
      setVideoUrl('');
    } catch (err) {
      setError(err.message);
      console.error('URL upload error:', err);
    } finally {
      setIsUploading(false);
    }
  };

  /**
   * Initialize video after upload
   */
  const initializeVideo = (data) => {
    setVideoId(data.video_id);
    setMetadata({
      filename: data.filename,
      duration: data.duration_seconds,
      fps: data.fps,
      resolution: data.resolution,
      totalFrames: data.total_frames,
      source: data.source,
    });

    // Reset tracks for new video
    playerTracksRef.current.clear();
    setStats({ frameIdx: 0, totalPlayers: 0, fps: 0, timestamp: 0, proximities: 0 });

    // Auto-connect to WebSocket
    setTimeout(() => connectWebSocket(data.video_id), 500);
  };

  /**
   * Connect to WebSocket stream
   */
  const connectWebSocket = (vId) => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/videos/ws/stream/${vId}`;

    try {
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsStreaming(true);
        setError(null);
      };

      ws.onmessage = (event) => {
        const message = JSON.parse(event.data);

        if (message.type === 'metadata') {
          setMetadata((prev) => ({
            ...prev,
            duration: message.duration_seconds,
            fps: message.fps,
            totalFrames: message.total_frames,
            resolution: message.resolution,
            teamNames: message.team_names,
            source: message.source,
          }));
          if (message.team_names) {
            setTeamNames(message.team_names);
          }
        } else if (message.type === 'frame_data') {
          setStats({
            frameIdx: message.frame_idx,
            timestamp: message.timestamp,
            totalPlayers: message.total_players,
            fps: metadata?.fps || 30,
            proximities: message.proximities?.length || 0,
          });

          renderFrame(
            {
              frame_idx: message.frame_idx,
              timestamp: message.timestamp,
              teams: message.teams,
              total_players: message.total_players,
            },
            message.proximities
          );

          lastFrameRef.current = message;
        } else if (message.type === 'complete') {
          console.log('Stream complete:', message.message);
          setIsStreaming(false);
        } else if (message.type === 'error') {
          setError(message.message);
          setIsStreaming(false);
        }
      };

      ws.onerror = (err) => {
        console.error('WebSocket error:', err);
        setError('WebSocket connection error');
        setIsStreaming(false);
      };

      ws.onclose = () => {
        console.log('WebSocket closed');
        setIsStreaming(false);
      };

      wsRef.current = ws;
    } catch (err) {
      setError(err.message);
      console.error('WebSocket connection error:', err);
    }
  };

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  /**
   * Initialize canvas
   */
  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      const rect = canvas.parentElement?.getBoundingClientRect();
      if (rect) {
        canvas.width = rect.width;
        canvas.height = rect.height;

        // Draw initial field
        const ctx = canvas.getContext('2d');
        drawField(ctx, canvas.width, canvas.height);

        // Set high DPI for retina displays
        const dpr = window.devicePixelRatio || 1;
        if (dpr > 1) {
          canvas.width = rect.width * dpr;
          canvas.height = rect.height * dpr;
          ctx.scale(dpr, dpr);
        }
      }
    }

    const handleResize = () => {
      if (canvas) {
        const rect = canvas.parentElement?.getBoundingClientRect();
        if (rect) {
          canvas.width = rect.width;
          canvas.height = rect.height;

          const dpr = window.devicePixelRatio || 1;
          if (dpr > 1) {
            canvas.width = rect.width * dpr;
            canvas.height = rect.height * dpr;
            canvas.getContext('2d').scale(dpr, dpr);
          }

          if (lastFrameRef.current) {
            renderFrame(
              {
                frame_idx: lastFrameRef.current.frame_idx,
                timestamp: lastFrameRef.current.timestamp,
                teams: lastFrameRef.current.teams,
                total_players: lastFrameRef.current.total_players,
              },
              lastFrameRef.current.proximities
            );
          } else {
            const ctx = canvas.getContext('2d');
            drawField(ctx, rect.width, rect.height);
          }
        }
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className="video-analysis-streaming">
      <div className="streaming-header">
        <h2>⚽ Real-time Video Analysis</h2>
        <p>Upload a video via file or URL to visualize player movements in real-time</p>
      </div>

      <div className="upload-section">
        <div className="upload-mode-toggle">
          <button
            className={`mode-btn ${uploadMode === 'file' ? 'active' : ''}`}
            onClick={() => setUploadMode('file')}
            disabled={isUploading || isStreaming}
          >
            📁 File Upload
          </button>
          <button
            className={`mode-btn ${uploadMode === 'url' ? 'active' : ''}`}
            onClick={() => setUploadMode('url')}
            disabled={isUploading || isStreaming}
          >
            🔗 URL
          </button>
        </div>

        {uploadMode === 'file' && (
          <div className="upload-input-wrapper">
            <input
              ref={uploadInputRef}
              type="file"
              accept="video/mp4,video/avi,video/quicktime"
              onChange={handleVideoUpload}
              disabled={isUploading || isStreaming}
              className="upload-input"
              id="video-upload"
            />
            <label htmlFor="video-upload" className="upload-label">
              {isUploading ? '📤 Uploading...' : '📁 Choose Video'}
            </label>
          </div>
        )}

        {uploadMode === 'url' && (
          <div className="url-input-wrapper">
            <input
              type="text"
              placeholder="Enter video URL (e.g., https://example.com/video.mp4)"
              value={videoUrl}
              onChange={(e) => setVideoUrl(e.target.value)}
              disabled={isUploading || isStreaming}
              className="url-input"
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleUrlSubmit();
                }
              }}
            />
            <button
              onClick={handleUrlSubmit}
              disabled={isUploading || isStreaming || !videoUrl.trim()}
              className="upload-label"
            >
              {isUploading ? '📤 Loading...' : '🚀 Load'}
            </button>
          </div>
        )}

        {videoId && metadata && (
          <div className="video-info">
            <div className="info-item">
              <span className="label">File:</span>
              <span>{metadata.filename}</span>
            </div>
            <div className="info-item">
              <span className="label">Duration:</span>
              <span>{metadata.duration?.toFixed(1)}s</span>
            </div>
            <div className="info-item">
              <span className="label">Resolution:</span>
              <span>{metadata.resolution}</span>
            </div>
            <div className="info-item">
              <span className="label">FPS:</span>
              <span>{metadata.fps}</span>
            </div>
            {metadata.source && (
              <div className="info-item">
                <span className="label">Source:</span>
                <span className="source-badge">{metadata.source.toUpperCase()}</span>
              </div>
            )}
          </div>
        )}

        {isStreaming && (
          <div className="streaming-indicator">
            <span className="pulse">●</span> Streaming Live
          </div>
        )}
      </div>

      <div className="canvas-container">
        <canvas ref={canvasRef} className="streaming-canvas" />
        {!videoId && (
          <div className="canvas-placeholder">
            Upload a video to start visualization
          </div>
        )}
      </div>

      <div className="stats-panel">
        <div className="stat-item">
          <span className="stat-label">Frame:</span>
          <span className="stat-value">{stats.frameIdx}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Time:</span>
          <span className="stat-value">{stats.timestamp.toFixed(2)}s</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Players:</span>
          <span className="stat-value">{stats.totalPlayers}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">FPS:</span>
          <span className="stat-value">{stats.fps}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Proximities:</span>
          <span className="stat-value">{stats.proximities}</span>
        </div>
      </div>

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      <div className="legend">
        <div className="legend-item">
          <div className="color-box" style={{ backgroundColor: '#E63946' }} />
          <span>{teamNames['0'] || 'Team A'} (Red)</span>
        </div>
        <div className="legend-item">
          <div className="color-box" style={{ backgroundColor: '#457B9D' }} />
          <span>{teamNames['1'] || 'Team B'} (Blue)</span>
        </div>
        <div className="legend-item">
          <div className="color-box" style={{ backgroundColor: '#FFD60A' }} />
          <span>Proximity</span>
        </div>
        <div className="legend-item">
          <div className="color-box" style={{ backgroundColor: 'rgba(255, 255, 255, 0.3)' }} />
          <span>Trail</span>
        </div>
      </div>
    </div>
  );
};

export default VideoAnalysisStreaming;
