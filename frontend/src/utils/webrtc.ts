export const getWebSocketStatus = (readyState: WebSocket['readyState']) => {
  if (readyState === WebSocket.OPEN)
    return { label: '연결됨', color: 'text-green-400' };
  if (readyState === WebSocket.CONNECTING)
    return { label: '연결중', color: 'text-yellow-400' };
  return { label: '연결 끊김', color: 'text-red-400' };
};

export const isSystemOnline = (
  readyState: WebSocket['readyState'],
  targetCamState: RTCIceConnectionState,
  shooterCamState: RTCIceConnectionState
) => {
  return (
    readyState === WebSocket.OPEN &&
    (targetCamState === 'connected' || targetCamState === 'completed') &&
    (shooterCamState === 'connected' || shooterCamState === 'completed')
  );
};

export const getStateColor = (state: RTCIceConnectionState) => {
  switch (state) {
    case 'connected':
    case 'completed':
      return 'text-green-400';
    case 'checking':
    case 'new':
      return 'text-yellow-400';
    case 'disconnected':
    case 'failed':
    case 'closed':
      return 'text-red-400';
    default:
      return 'text-gray-400';
  }
};

export const getStateLabel = (state: RTCIceConnectionState) => {
  switch (state) {
    case 'connected':
    case 'completed':
      return '연결됨';
    case 'checking':
      return '연결중';
    case 'new':
      return '대기';
    case 'disconnected':
      return '끊김';
    case 'failed':
      return '실패';
    case 'closed':
      return '종료';
    default:
      return state;
  }
};
