/**
 * Video Analysis Page - Real-time streaming and visualization
 *
 * Provides interface for uploading videos and visualizing player movements
 * in real-time through WebSocket streaming.
 */
import VideoAnalysisStreaming from '../components/VideoAnalysisStreaming';
import './VideoAnalysis.css';

export default function VideoAnalysis() {
  return (
    <div className="video-analysis-page">
      <VideoAnalysisStreaming />
    </div>
  );
}
