"""API Routes for Real-time Video Analysis

Endpoints para upload e processamento de vídeos com streaming de movimentações.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Optional
import tempfile

from ..video_analysis.video_processor import VideoStreamProcessor, RealTimeGraphBuilder

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/videos", tags=["video-analysis"])

# Armazenar processadores ativos
active_processors: dict = {}


@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    team_names: Optional[str] = Query(None),
):
    """Upload de vídeo para análise.

    Args:
        file: Arquivo de vídeo (MP4, AVI, MOV)
        team_names: JSON com nomes dos times {"0": "Flamengo", "1": "Botafogo"}

    Returns:
        {
            "video_id": "uuid",
            "filename": "video.mp4",
            "size_bytes": 5242880,
            "status": "uploaded"
        }
    """
    try:
        # Salvar arquivo temporário
        temp_dir = tempfile.gettempdir()
        video_path = os.path.join(temp_dir, file.filename)

        with open(video_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Obter metadados
        processor = VideoStreamProcessor()
        metadata = processor.get_video_metadata(video_path)

        # Gerar ID único
        video_id = Path(video_path).stem

        # Armazenar para próximas operações
        active_processors[video_id] = {
            "path": video_path,
            "metadata": metadata,
            "processor": processor,
            "graph_builder": RealTimeGraphBuilder(),
        }

        return JSONResponse({
            "video_id": video_id,
            "filename": file.filename,
            "size_bytes": len(content),
            "duration_seconds": metadata.duration_seconds,
            "fps": metadata.fps,
            "resolution": f"{metadata.width}x{metadata.height}",
            "total_frames": metadata.total_frames,
            "status": "uploaded",
        })

    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream/{video_id}")
async def get_video_stream(video_id: str):
    """Stream de vídeo processado.

    Returns:
        Vídeo com anotações de detecções
    """
    if video_id not in active_processors:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")

    processor_info = active_processors[video_id]
    video_path = processor_info["path"]

    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Arquivo de vídeo não encontrado")

    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"video_{video_id}.mp4"
    )


@router.websocket("/ws/stream/{video_id}")
async def websocket_stream(websocket: WebSocket, video_id: str):
    """WebSocket para streaming em tempo real de movimentações.

    Envia dados de rastreamento frame-by-frame:
    {
        "frame_idx": 120,
        "timestamp": 4.0,
        "teams": {
            "0": [
                {"player_id": 0, "x": 150.5, "y": 200.3, "trajectory": [[...], [...]]},
                ...
            ]
        },
        "proximities": [
            {"source": 0, "target": 5, "distance": 45.2, "same_team": true}
        ]
    }
    """
    if video_id not in active_processors:
        await websocket.close(code=4004, reason="Vídeo não encontrado")
        return

    await websocket.accept()
    logger.info(f"WebSocket conectado: {video_id}")

    processor_info = active_processors[video_id]
    processor = processor_info["processor"]
    graph_builder = processor_info["graph_builder"]
    video_path = processor_info["path"]

    skip_frames = 1  # Processar todos os frames

    try:
        # Função callback para enviar dados ao cliente
        def frame_callback(frame_data):
            # Atualizar grafo
            graph_builder.update(frame_data)

            # Obter dados do grafo
            graph_data = graph_builder.get_current_graph_data()
            proximities = graph_builder.calculate_proximities()

            # Preparar mensagem
            message = {
                "type": "frame_data",
                "frame_idx": frame_data.frame_idx,
                "timestamp": frame_data.timestamp,
                "data": graph_data,
                "proximities": proximities,
            }

            # Enviar via WebSocket (será feito de forma assíncrona)
            return message

        # Processar vídeo
        metadata = processor.get_video_metadata(video_path)

        # Enviar metadados
        await websocket.send_json({
            "type": "metadata",
            "duration_seconds": metadata.duration_seconds,
            "fps": metadata.fps,
            "total_frames": metadata.total_frames,
            "resolution": f"{metadata.width}x{metadata.height}",
        })

        # Processar e enviar frame a frame
        import cv2
        cap = cv2.VideoCapture(video_path)

        frame_idx = 0
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_idx % skip_frames != 0:
                    frame_idx += 1
                    continue

                # Simular detecção
                from .video_analysis.video_processor import FrameData

                player_positions = processor._simulate_player_detection(frame, frame_idx)

                frame_data = FrameData(
                    frame_idx=frame_idx,
                    timestamp=frame_idx / metadata.fps,
                    player_positions=player_positions,
                    detections_count=len(player_positions),
                )

                # Atualizar grafo
                graph_builder.update(frame_data)

                # Obter dados
                graph_data = graph_builder.get_current_graph_data()
                proximities = graph_builder.calculate_proximities()

                # Enviar
                await websocket.send_json({
                    "type": "frame_data",
                    "frame_idx": frame_data.frame_idx,
                    "timestamp": frame_data.timestamp,
                    "teams": graph_data.get("teams", {}),
                    "total_players": graph_data.get("total_players", 0),
                    "proximities": proximities,
                })

                # Simular delay de processamento
                await asyncio.sleep(0.01)

                frame_idx += 1

        finally:
            cap.release()

        # Enviar fim do vídeo
        await websocket.send_json({
            "type": "complete",
            "total_frames": frame_idx,
            "message": "Vídeo processado com sucesso",
        })

    except WebSocketDisconnect:
        logger.info(f"WebSocket desconectado: {video_id}")
    except Exception as e:
        logger.error(f"Erro no WebSocket: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e),
            })
        except:
            pass


@router.get("/status/{video_id}")
async def get_video_status(video_id: str):
    """Status de processamento de um vídeo.

    Returns:
        {
            "video_id": "video",
            "status": "uploaded | processing | completed",
            "metadata": {...}
        }
    """
    if video_id not in active_processors:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")

    processor_info = active_processors[video_id]
    metadata = processor_info["metadata"]

    return JSONResponse({
        "video_id": video_id,
        "status": "ready",
        "metadata": {
            "duration_seconds": metadata.duration_seconds,
            "fps": metadata.fps,
            "total_frames": metadata.total_frames,
            "resolution": f"{metadata.width}x{metadata.height}",
        }
    })


@router.delete("/clean/{video_id}")
async def clean_video(video_id: str):
    """Deletar vídeo e limpar recursos.

    Args:
        video_id: ID do vídeo

    Returns:
        {"status": "cleaned", "video_id": "video"}
    """
    if video_id not in active_processors:
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")

    try:
        processor_info = active_processors[video_id]
        video_path = processor_info["path"]

        # Deletar arquivo
        if os.path.exists(video_path):
            os.remove(video_path)

        # Remover do cache
        del active_processors[video_id]

        return JSONResponse({
            "status": "cleaned",
            "video_id": video_id,
        })

    except Exception as e:
        logger.error(f"Erro ao limpar vídeo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ["router"]
